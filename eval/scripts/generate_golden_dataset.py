#!/usr/bin/env python3
"""
Generate Golden Dataset using RAGAS Knowledge Graphs

This script uses RAGAS TestsetGenerator to create synthetic test scenarios
from the existing chunked federal ethics documents, then generates corresponding
ground truth answers in markdown format.
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "api"))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from ragas.testset import TestsetGenerator
import tiktoken

from api.app.core.logging_config import configure_logging, get_logger
from api.app.core.settings import settings
from api.app.services.document_loader_service import DocumentLoaderService
from api.app.services.ethics_assessment_service import EthicsAssessmentService

# Load environment variables
load_dotenv(".env.local")

# Configure logging
configure_logging()
logger = get_logger("eval.generate_golden_dataset")


class GoldenDatasetGenerator:
    """Generate comprehensive golden dataset using RAGAS knowledge graphs with in-memory vector store"""
    
    def __init__(self):
        # Initialize models for dataset generation using settings
        self.generator_llm = ChatOpenAI(
            model=settings.ragas_generator_model,
            temperature=settings.ragas_generator_temperature,
            api_key=settings.openai_api_key
        )
        
        self.generator_embeddings = OpenAIEmbeddings(
            model=settings.ragas_embedding_model,
            api_key=settings.openai_api_key
        )
        
        # Initialize services
        self.document_loader = DocumentLoaderService()
        self.ethics_assessor = EthicsAssessmentService()
        
        # Initialize in-memory Qdrant client
        self.qdrant_client = QdrantClient(":memory:")
        self.collection_name = "ethics_knowledge_temp"
        self.vector_store = None
        
        # Initialize text splitter with tiktoken
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=self._tiktoken_len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize TestsetGenerator
        self.testset_generator = TestsetGenerator(
            llm=self.generator_llm,
            embedding_model=self.generator_embeddings
        )
    
    def _tiktoken_len(self, text: str) -> int:
        """Calculate text length using tiktoken"""
        return len(self.encoding.encode(text))
    
    def load_and_chunk_documents(self) -> List[Document]:
        """Load raw documents and chunk them for vector storage"""
        logger.info("Loading and chunking federal ethics documents")
        
        try:
            # Load raw documents (full pages, not pre-chunked)
            data_dir = Path(project_root) / "data"
            documents = []
            
            # Process PDF files in data directory
            for pdf_file in data_dir.glob("*.pdf"):
                logger.info(f"Processing {pdf_file.name}")
                
                # Load document content using PyMuPDF (same as DocumentLoaderService)
                import pymupdf
                doc = pymupdf.open(pdf_file)
                full_text = ""
                total_pages = len(doc)
                
                for page_num in range(total_pages):
                    page = doc[page_num]
                    full_text += page.get_text()
                
                doc.close()
                
                # Create document with metadata
                raw_document = Document(
                    page_content=full_text,
                    metadata={
                        "source": str(pdf_file),
                        "filename": pdf_file.name,
                        "total_pages": total_pages
                    }
                )
                documents.append(raw_document)
            
            # Chunk all documents
            logger.info(f"Chunking {len(documents)} documents")
            all_chunks = []
            
            for doc in documents:
                chunks = self.text_splitter.split_documents([doc])
                logger.info(f"Created {len(chunks)} chunks from {doc.metadata.get('filename', 'unknown')}")
                all_chunks.extend(chunks)
            
            logger.info(f"Total chunks created: {len(all_chunks)}")
            return all_chunks
            
        except Exception as e:
            logger.error(f"Failed to load and chunk documents: {e}")
            return []
    
    def create_vector_store(self, documents: List[Document]) -> QdrantVectorStore:
        """Create in-memory vector store with chunked documents"""
        logger.info(f"Creating in-memory vector store with {len(documents)} chunks")
        
        try:
            # Create collection
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            
            # Create vector store
            vector_store = QdrantVectorStore(
                client=self.qdrant_client,
                collection_name=self.collection_name,
                embedding=self.generator_embeddings
            )
            
            # Add documents to vector store
            logger.info("Embedding and indexing documents...")
            vector_store.add_documents(documents)
            
            logger.info(f"Vector store created with {len(documents)} indexed chunks")
            self.vector_store = vector_store
            return vector_store
            
        except Exception as e:
            logger.error(f"Failed to create vector store: {e}")
            raise
    
    def retrieve_relevant_context(self, query: str, k: int = 10) -> List[Document]:
        """Retrieve relevant context for test generation"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            # Use similarity search to get relevant chunks
            relevant_docs = self.vector_store.similarity_search(query, k=k)
            logger.debug(f"Retrieved {len(relevant_docs)} relevant chunks for query: {query[:100]}...")
            return relevant_docs
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    
    def generate_synthetic_scenarios(self, documents: List, testset_size: int = 15) -> List[Dict[str, Any]]:
        """Generate synthetic test scenarios using RAGAS knowledge graphs"""
        logger.info(f"Generating {testset_size} synthetic scenarios from {len(documents)} documents")
        
        try:
            # Use configured subset of documents for generation
            doc_subset = documents[:settings.ragas_document_subset_size]
            
            logger.info(f"Using {len(doc_subset)} document chunks for generation")
            
            # Generate dataset with RAGAS TestsetGenerator
            dataset = self.testset_generator.generate_with_langchain_docs(
                doc_subset, 
                testset_size=testset_size
            )
            
            # Convert to list of dictionaries
            scenarios = []
            for i, item in enumerate(dataset):
                scenario = {
                    "id": f"kg_generated_{i+1}",
                    "question": getattr(item, 'question', str(item)),
                    "ground_truth": getattr(item, 'ground_truth', ''),
                    "contexts": getattr(item, 'contexts', []),
                    "evolution_type": getattr(item, 'evolution_type', 'unknown'),
                    "metadata": getattr(item, 'metadata', {})
                }
                scenarios.append(scenario)
            
            logger.info(f"Successfully generated {len(scenarios)} scenarios")
            return scenarios
            
        except Exception as e:
            logger.error(f"Failed to generate synthetic scenarios: {e}")
            return []
    
    async def generate_ground_truth_answers(self, scenarios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate comprehensive ground truth answers in markdown format"""
        logger.info(f"Generating ground truth answers for {len(scenarios)} scenarios")
        
        enhanced_scenarios = []
        
        for i, scenario in enumerate(scenarios):
            try:
                logger.info(f"Processing scenario {i+1}/{len(scenarios)}")
                
                # Create comprehensive ground truth using our ethics assessment service
                # Use the original contexts as federal_context
                federal_context = "\n\n".join(scenario.get("contexts", []))
                
                # Generate comprehensive markdown assessment
                ground_truth_answer = self.ethics_assessor.assess_ethics_scenario(
                    question=scenario["question"],
                    search_plan="Knowledge graph generated scenario assessment",
                    user_context={"role": "federal_employee", "agency": "General", "seniority": "mid_level"},
                    federal_context=federal_context,
                    general_results="",  # No web search for ground truth generation
                    penalty_results="",
                    guidance_results=""
                )
                
                # Use configured user context variations for diversity
                enhanced_scenario = {
                    "question": scenario["question"],
                    "user_context": settings.user_contexts[i % len(settings.user_contexts)],
                    "ground_truth": ground_truth_answer,
                    "contexts": scenario.get("contexts", []),
                    "evolution_type": scenario.get("evolution_type", "unknown"),
                    "generation_metadata": {
                        "generated_by": "ragas_knowledge_graph",
                        "original_ground_truth": scenario.get("ground_truth", ""),
                        "enhanced_at": datetime.now().isoformat()
                    }
                }
                
                enhanced_scenarios.append(enhanced_scenario)
                
                # Rate limiting from configuration
                await asyncio.sleep(settings.ground_truth_rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Failed to generate ground truth for scenario {i+1}: {e}")
                # Add fallback scenario
                enhanced_scenarios.append({
                    "question": scenario["question"],
                    "user_context": {"role": "federal_employee", "agency": "General", "seniority": "mid_level"},
                    "ground_truth": scenario.get("ground_truth", "Assessment not available"),
                    "contexts": scenario.get("contexts", []),
                    "error": str(e)
                })
        
        logger.info(f"Generated ground truth answers for {len(enhanced_scenarios)} scenarios")
        return enhanced_scenarios
    
    def save_dataset(self, dataset: List[Dict[str, Any]], filename: str = None) -> str:
        """Save the generated dataset to configured directory"""
        if filename is None:
            if settings.dataset_include_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{settings.dataset_filename_prefix}_{timestamp}.json"
            else:
                filename = f"{settings.dataset_filename_prefix}.json"
        
        output_dir = Path(settings.dataset_output_directory)
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved golden dataset to {filepath}")
        return str(filepath)
    
    async def generate_full_dataset(self, testset_size: int = 15) -> str:
        """Generate complete golden dataset with knowledge graphs using in-memory vector store"""
        logger.info("Starting full golden dataset generation process with vector store")
        
        try:
            # Step 1: Load and chunk documents
            logger.info("Step 1: Loading and chunking documents...")
            chunked_documents = self.load_and_chunk_documents()
            if not chunked_documents:
                raise Exception("No documents loaded or chunked")
            
            # Step 2: Create in-memory vector store
            logger.info("Step 2: Creating in-memory vector store...")
            self.create_vector_store(chunked_documents)
            
            # Step 3: Use subset for RAGAS generation (for efficiency)
            logger.info("Step 3: Preparing documents for RAGAS...")
            doc_subset = chunked_documents[:settings.ragas_document_subset_size]
            
            # Step 4: Generate synthetic scenarios using RAGAS
            logger.info("Step 4: Generating synthetic scenarios...")
            scenarios = self.generate_synthetic_scenarios(doc_subset, testset_size)
            if not scenarios:
                raise Exception("No scenarios generated")
            
            # Step 5: Enhance scenarios with vector store context
            logger.info("Step 5: Enhancing scenarios with vector store context...")
            enhanced_scenarios = []
            for scenario in scenarios:
                # Get additional context from vector store for each scenario
                vector_context = self.retrieve_relevant_context(scenario["question"], k=8)
                vector_context_text = [doc.page_content for doc in vector_context]
                
                # Combine original contexts with vector store context
                combined_contexts = list(scenario.get("contexts", [])) + vector_context_text
                # Remove duplicates while preserving order
                seen = set()
                unique_contexts = []
                for ctx in combined_contexts:
                    if ctx not in seen:
                        seen.add(ctx)
                        unique_contexts.append(ctx)
                
                enhanced_scenario = scenario.copy()
                enhanced_scenario["contexts"] = unique_contexts[:10]  # Limit to top 10
                enhanced_scenarios.append(enhanced_scenario)
            
            # Step 6: Generate comprehensive ground truth answers
            logger.info("Step 6: Generating ground truth answers...")
            enhanced_dataset = await self.generate_ground_truth_answers(enhanced_scenarios)
            
            # Step 7: Save dataset
            logger.info("Step 7: Saving dataset...")
            filepath = self.save_dataset(enhanced_dataset)
            
            # Step 8: Generate summary
            summary = {
                "total_scenarios": len(enhanced_dataset),
                "document_chunks_used": len(chunked_documents),
                "vector_store_chunks": len(chunked_documents),
                "ragas_subset_size": len(doc_subset),
                "generation_timestamp": datetime.now().isoformat(),
                "successful_generations": len([s for s in enhanced_dataset if "error" not in s]),
                "failed_generations": len([s for s in enhanced_dataset if "error" in s])
            }
            
            logger.info("Golden dataset generation completed", extra=summary)
            print(f"\n🎉 Golden Dataset Generation Complete!")
            print(f"📊 Generated {summary['total_scenarios']} scenarios")
            print(f"📁 Saved to: {filepath}")
            print(f"🗃️  Vector store: {summary['vector_store_chunks']} chunks indexed")
            print(f"✅ Successful: {summary['successful_generations']}")
            print(f"❌ Failed: {summary['failed_generations']}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate golden dataset: {e}")
            raise


async def main():
    """Main execution function"""
    print("🔧 Federal Ethics Golden Dataset Generator")
    print("Using In-Memory Vector Store + RAGAS Knowledge Graphs + Comprehensive Ground Truth")
    print("=" * 80)
    
    generator = GoldenDatasetGenerator()
    
    try:
        # Generate dataset with configured testset size
        dataset_path = await generator.generate_full_dataset(testset_size=settings.ragas_testset_size)
        print(f"\n✅ Dataset generated successfully: {dataset_path}")
        
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())