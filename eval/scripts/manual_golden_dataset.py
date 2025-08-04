#!/usr/bin/env python3
"""
Create Golden Dataset Manually from Ethics Documents

Since RAGAS TestsetGenerator is having issues with document transformation,
this approach manually creates diverse test scenarios from the existing
chunked ethics documents and generates comprehensive ground truth answers.
"""

import sys
import asyncio
import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "api"))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import tiktoken

from api.app.core.logging_config import configure_logging, get_logger
from api.app.core.settings import settings
from api.app.services.document_loader_service import DocumentLoaderService
from api.app.services.ethics_assessment_service import EthicsAssessmentService

# Load environment variables
load_dotenv(".env.local")

# Configure logging
configure_logging()
logger = get_logger("eval.create_manual_golden_dataset")


class ManualGoldenDatasetGenerator:
    """Generate golden dataset manually with in-memory vector store for enhanced context"""
    
    def __init__(self):
        # Initialize services
        self.document_loader = DocumentLoaderService()
        self.ethics_assessor = EthicsAssessmentService()
        
        # Initialize scenario generation model
        self.scenario_generator = ChatOpenAI(
            model=settings.ragas_generator_model,
            temperature=settings.ragas_generator_temperature,
            api_key=settings.openai_api_key
        )
        
        # Initialize embeddings for vector store
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key
        )
        
        # Initialize in-memory Qdrant client
        self.qdrant_client = QdrantClient(":memory:")
        self.collection_name = "ethics_manual_temp"
        self.vector_store = None
        
        # Initialize text splitter with tiktoken
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=self._tiktoken_len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self._setup_scenario_generator()
    
    def _tiktoken_len(self, text: str) -> int:
        """Calculate text length using tiktoken"""
        return len(self.encoding.encode(text))
    
    def _setup_scenario_generator(self):
        """Setup prompt template for scenario generation"""
        scenario_template = """
        You are a federal ethics expert creating realistic ethics scenarios for government employees.
        
        Based on this federal ethics law content, create a realistic ethics question that a federal employee might ask:
        
        ETHICS LAW CONTENT:
        {content}
        
        USER CONTEXT:
        - Role: {role}
        - Agency: {agency}  
        - Seniority: {seniority}
        - Clearance: {clearance}
        
        Create a specific, realistic scenario question that:
        1. Is relevant to the user's role and agency
        2. References the ethics law content provided
        3. Is something a real federal employee might encounter
        4. Is clear and specific (not vague or hypothetical)
        5. Is 50-200 words long
        
        Return only the question, no additional text.
        """
        
        self.scenario_chain = (
            ChatPromptTemplate.from_template(scenario_template) |
            self.scenario_generator
        )
    
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
                embedding=self.embeddings
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
    
    def retrieve_relevant_context(self, query: str, k: int = 5) -> List[Document]:
        """Retrieve relevant context for enhanced ground truth generation"""
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
    
    
    def generate_scenario_from_document(self, document, user_context: Dict[str, str]) -> str:
        """Generate a realistic scenario question from a document chunk"""
        try:
            response = self.scenario_chain.invoke({
                "content": document.page_content,
                "role": user_context["role"],
                "agency": user_context["agency"],
                "seniority": user_context["seniority"],
                "clearance": user_context["clearance"]
            })
            return response.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate scenario: {e}")
            return ""
    
    async def create_diverse_scenarios(self, documents: List, num_scenarios: int) -> List[Dict[str, Any]]:
        """Create diverse test scenarios from document chunks"""
        logger.info(f"Creating {num_scenarios} diverse scenarios from {len(documents)} documents")
        
        scenarios = []
        user_contexts = settings.user_contexts
        
        # Select diverse document chunks
        selected_docs = random.sample(documents, min(len(documents), num_scenarios * 2))
        
        for i in range(num_scenarios):
            try:
                # Rotate through user contexts for diversity
                user_context = user_contexts[i % len(user_contexts)]
                
                # Select document for this scenario
                doc = selected_docs[i % len(selected_docs)]
                
                logger.info(f"Generating scenario {i+1}/{num_scenarios}")
                
                # Generate scenario question
                question = self.generate_scenario_from_document(doc, user_context)
                
                if not question:
                    logger.warning(f"Empty question generated for scenario {i+1}")
                    continue
                
                # Get additional context from vector store
                additional_context = self.retrieve_relevant_context(question, k=8)
                additional_context_text = [d.page_content for d in additional_context]
                
                # Combine original document with vector store context
                combined_context = [doc.page_content] + additional_context_text
                # Remove duplicates while preserving order
                seen = set()
                unique_context = []
                for ctx in combined_context:
                    if ctx not in seen:
                        seen.add(ctx)
                        unique_context.append(ctx)
                
                # Use combined context for ground truth generation
                federal_context = "\n\n".join(unique_context[:5])  # Limit to top 5 for token efficiency
                
                # Generate comprehensive ground truth answer
                ground_truth = self.ethics_assessor.assess_ethics_scenario(
                    question=question,
                    search_plan="Manual golden dataset generation with vector store context",
                    user_context=user_context,
                    federal_context=federal_context,
                    general_results="",
                    penalty_results="",
                    guidance_results=""
                )
                
                scenario = {
                    "question": question,
                    "user_context": user_context,
                    "ground_truth": ground_truth,
                    "contexts": unique_context[:5],  # Include enhanced context
                    "source_document": {
                        "metadata": doc.metadata,
                        "chunk_preview": doc.page_content[:200] + "..."
                    },
                    "generation_metadata": {
                        "method": "manual_from_document_with_vector_store",
                        "generated_at": datetime.now().isoformat(),
                        "scenario_id": f"manual_{i+1:03d}",
                        "vector_store_chunks_used": len(additional_context),
                        "total_context_chunks": len(unique_context)
                    }
                }
                
                scenarios.append(scenario)
                
                # Rate limiting
                await asyncio.sleep(settings.ground_truth_rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Failed to create scenario {i+1}: {e}")
                continue
        
        logger.info(f"Successfully created {len(scenarios)} scenarios")
        return scenarios
    
    def save_dataset(self, dataset: List[Dict[str, Any]]) -> str:
        """Save the generated dataset"""
        if settings.dataset_include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{settings.dataset_filename_prefix}_manual_{timestamp}.json"
        else:
            filename = f"{settings.dataset_filename_prefix}_manual.json"
        
        output_dir = Path(settings.dataset_output_directory)
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved golden dataset to {filepath}")
        return str(filepath)
    
    async def generate_full_dataset(self) -> str:
        """Generate complete golden dataset manually with in-memory vector store"""
        logger.info("Starting manual golden dataset generation with vector store")
        
        try:
            # Step 1: Load and chunk documents
            logger.info("Step 1: Loading and chunking documents...")
            chunked_documents = self.load_and_chunk_documents()
            if not chunked_documents:
                raise Exception("No documents loaded or chunked")
            
            # Step 2: Create in-memory vector store
            logger.info("Step 2: Creating in-memory vector store...")
            self.create_vector_store(chunked_documents)
            
            # Step 3: Create diverse scenarios with vector store enhancement
            logger.info("Step 3: Creating diverse scenarios...")
            scenarios = await self.create_diverse_scenarios(
                chunked_documents, 
                settings.ragas_testset_size
            )
            
            if not scenarios:
                raise Exception("No scenarios created")
            
            # Step 4: Save dataset
            logger.info("Step 4: Saving dataset...")
            filepath = self.save_dataset(scenarios)
            
            # Step 5: Generate summary
            summary = {
                "total_scenarios": len(scenarios),
                "document_chunks_available": len(chunked_documents),
                "vector_store_chunks": len(chunked_documents),
                "generation_method": "manual_from_documents_with_vector_store",
                "generation_timestamp": datetime.now().isoformat(),
                "user_contexts_used": len(settings.user_contexts),
                "successful_generations": len([s for s in scenarios if "generation_metadata" in s]),
                "vector_store_enhanced": True
            }
            
            logger.info("Manual golden dataset generation completed", extra=summary)
            print(f"\n🎉 Manual Golden Dataset Generation Complete!")
            print(f"📊 Generated {summary['total_scenarios']} scenarios")
            print(f"📁 Saved to: {filepath}")
            print(f"🗃️  Vector store: {summary['vector_store_chunks']} chunks indexed")
            print(f"👥 Used {summary['user_contexts_used']} different user contexts")
            print(f"📚 Drew from {summary['document_chunks_available']} document chunks")
            print(f"🚀 Vector store enhanced: {summary['vector_store_enhanced']}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate manual golden dataset: {e}")
            raise


async def main():
    """Main execution function"""
    print("🔧 Manual Federal Ethics Golden Dataset Generator")
    print("Creating realistic scenarios from federal ethics documents")
    print("=" * 60)
    
    generator = ManualGoldenDatasetGenerator()
    
    try:
        dataset_path = await generator.generate_full_dataset()
        print(f"\n✅ Dataset generated successfully: {dataset_path}")
        
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())