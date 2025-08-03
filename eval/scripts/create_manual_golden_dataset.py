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
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

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
    """Generate golden dataset manually from ethics documents"""
    
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
        
        self._setup_scenario_generator()
    
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
    
    def load_ethics_documents(self) -> List:
        """Load ethics documents"""
        logger.info("Loading federal ethics documents")
        
        try:
            documents = self.document_loader.load_ethics_documents()
            logger.info(f"Loaded {len(documents)} document chunks")
            return documents
        except Exception as e:
            logger.error(f"Failed to load ethics documents: {e}")
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
                
                # Generate comprehensive ground truth answer
                ground_truth = self.ethics_assessor.assess_ethics_scenario(
                    question=question,
                    search_plan="Manual golden dataset generation",
                    user_context=user_context,
                    federal_context=doc.page_content,
                    general_results="",
                    penalty_results="",
                    guidance_results=""
                )
                
                scenario = {
                    "question": question,
                    "user_context": user_context,
                    "ground_truth": ground_truth,
                    "contexts": [doc.page_content],
                    "source_document": {
                        "metadata": doc.metadata,
                        "chunk_preview": doc.page_content[:200] + "..."
                    },
                    "generation_metadata": {
                        "method": "manual_from_document",
                        "generated_at": datetime.now().isoformat(),
                        "scenario_id": f"manual_{i+1:03d}"
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
        """Generate complete golden dataset manually"""
        logger.info("Starting manual golden dataset generation")
        
        try:
            # Load documents
            documents = self.load_ethics_documents()
            if not documents:
                raise Exception("No documents loaded")
            
            # Create diverse scenarios
            scenarios = await self.create_diverse_scenarios(
                documents, 
                settings.ragas_testset_size
            )
            
            if not scenarios:
                raise Exception("No scenarios created")
            
            # Save dataset
            filepath = self.save_dataset(scenarios)
            
            # Generate summary
            summary = {
                "total_scenarios": len(scenarios),
                "document_chunks_available": len(documents),
                "generation_method": "manual_from_documents",
                "generation_timestamp": datetime.now().isoformat(),
                "user_contexts_used": len(settings.user_contexts)
            }
            
            logger.info("Manual golden dataset generation completed", extra=summary)
            print(f"\n🎉 Manual Golden Dataset Generation Complete!")
            print(f"📊 Generated {summary['total_scenarios']} scenarios")
            print(f"📁 Saved to: {filepath}")
            print(f"👥 Used {summary['user_contexts_used']} different user contexts")
            print(f"📚 Drew from {summary['document_chunks_available']} document chunks")
            
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