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
from ragas.testset import TestsetGenerator

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
    """Generate comprehensive golden dataset using RAGAS knowledge graphs"""
    
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
        
        # Initialize TestsetGenerator
        self.testset_generator = TestsetGenerator(
            llm=self.generator_llm,
            embedding_model=self.generator_embeddings
        )
    
    def load_ethics_documents(self) -> List[Document]:
        """Load and return chunked ethics documents for RAGAS"""
        logger.info("Loading federal ethics documents for knowledge graph generation")
        
        try:
            # Load original documents
            original_documents = self.document_loader.load_ethics_documents()
            
            # Create new Documents with both page_content and content attributes for RAGAS
            ragas_compatible_docs = []
            for doc in original_documents:
                # Create a new Document with the same content
                new_doc = Document(
                    page_content=doc.page_content,
                    metadata=doc.metadata or {}
                )
                ragas_compatible_docs.append(new_doc)
            
            logger.info(f"Loaded {len(ragas_compatible_docs)} document chunks", extra={
                "total_chunks": len(ragas_compatible_docs),
                "sample_content_length": len(ragas_compatible_docs[0].page_content) if ragas_compatible_docs else 0
            })
            return ragas_compatible_docs
        except Exception as e:
            logger.error(f"Failed to load ethics documents: {e}")
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
        """Generate complete golden dataset with knowledge graphs"""
        logger.info("Starting full golden dataset generation process")
        
        try:
            # Step 1: Load ethics documents
            documents = self.load_ethics_documents()
            if not documents:
                raise Exception("No documents loaded")
            
            # Step 2: Generate synthetic scenarios using RAGAS
            scenarios = self.generate_synthetic_scenarios(documents, testset_size)
            if not scenarios:
                raise Exception("No scenarios generated")
            
            # Step 3: Generate comprehensive ground truth answers
            enhanced_dataset = await self.generate_ground_truth_answers(scenarios)
            
            # Step 4: Save dataset
            filepath = self.save_dataset(enhanced_dataset)
            
            # Step 5: Generate summary
            summary = {
                "total_scenarios": len(enhanced_dataset),
                "document_chunks_used": len(documents),
                "generation_timestamp": datetime.now().isoformat(),
                "successful_generations": len([s for s in enhanced_dataset if "error" not in s]),
                "failed_generations": len([s for s in enhanced_dataset if "error" in s])
            }
            
            logger.info("Golden dataset generation completed", extra=summary)
            print(f"\n🎉 Golden Dataset Generation Complete!")
            print(f"📊 Generated {summary['total_scenarios']} scenarios")
            print(f"📁 Saved to: {filepath}")
            print(f"✅ Successful: {summary['successful_generations']}")
            print(f"❌ Failed: {summary['failed_generations']}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate golden dataset: {e}")
            raise


async def main():
    """Main execution function"""
    print("🔧 Federal Ethics Golden Dataset Generator")
    print("Using RAGAS Knowledge Graphs + Comprehensive Ground Truth")
    print("=" * 60)
    
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