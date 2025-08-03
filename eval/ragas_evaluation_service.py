import json
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from datasets import Dataset
from datetime import datetime

from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness,
    answer_similarity
)

import sys
sys.path.append('../api')

from api.app.core.settings import settings
from api.app.core.logging_config import get_logger
from api.app.models.chat_models import ChatRequest, UserContext, UserRole
from api.app.services.agentic_workflow_service import AgenticWorkflowService

logger = get_logger("app.services.ragas_evaluation")


class RAGASEvaluationService:
    """Service for evaluating the ethics chatbot using RAGAS metrics"""

    def __init__(self):
        self.workflow_service = AgenticWorkflowService()
        self.metrics = [
            faithfulness,          # LLM output faithful to retrieved context
            answer_relevancy,      # Answer relevancy to the question
            context_precision,     # Precision of retrieved context
            context_recall,        # Recall of retrieved context
            answer_correctness,    # Correctness compared to ground truth
            answer_similarity      # Similarity to ground truth answer
        ]

    def load_test_dataset(self, dataset_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load test dataset from JSON file"""
        try:
            # Use configured path or default
            if dataset_path is None:
                dataset_path = settings.test_dataset_path
            
            # Convert to Path object - handle both absolute and relative paths
            dataset_file = Path(dataset_path)
            if not dataset_file.is_absolute():
                # Make relative to project root
                project_root = Path(__file__).parent.parent
                dataset_file = project_root / dataset_path
            
            logger.info("Looking for test dataset", extra={"path": str(dataset_file)})

            with open(dataset_file, 'r') as f:
                dataset = json.load(f)

            logger.info("Test dataset loaded", extra={"test_cases": len(dataset)})
            return dataset

        except Exception as e:
            logger.error("Failed to load test dataset", extra={"error": str(e), "attempted_path": str(dataset_file)})
            raise

    async def generate_responses(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate responses for all test cases using the workflow service"""
        responses = []

        for i, test_case in enumerate(test_cases):
            try:
                logger.info(f"Processing test case {i+1}/{len(test_cases)}",
                           extra={"question": test_case["question"][:100]})

                # Create request
                user_context = UserContext(**test_case["user_context"])
                request = ChatRequest(
                    question=test_case["question"],
                    user_context=user_context
                )

                # Get response from workflow
                response = self.workflow_service.process_ethics_consultation(request)

                # Extract retrieved contexts
                contexts = []
                if hasattr(response, 'search_results') and response.search_results:
                    contexts = [result.content for result in response.search_results if result.content]

                # If no web contexts, try to get federal law contexts
                if not contexts and hasattr(self.workflow_service, 'vector_store'):
                    federal_docs = self.workflow_service.vector_store.search_similar_documents(
                        test_case["question"], top_k=3
                    )
                    contexts = [doc.page_content for doc in federal_docs]

                response_data = {
                    "question": test_case["question"],
                    "answer": response.response,
                    "contexts": contexts,
                    "ground_truth": test_case["ground_truth"],
                    "processing_time": response.processing_time_seconds,
                    "federal_sources": response.federal_law_sources,
                    "web_sources": response.web_sources,
                    "expected_violations": test_case.get("expected_violations", []),
                    "expected_severity": test_case.get("expected_severity", ""),
                    "expected_actions": test_case.get("expected_actions", [])
                }

                responses.append(response_data)

                # Add delay to avoid rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Failed to process test case {i+1}",
                           extra={"error": str(e), "question": test_case["question"][:100]})
                # Add placeholder response to maintain alignment
                responses.append({
                    "question": test_case["question"],
                    "answer": f"Error processing: {str(e)}",
                    "contexts": [],
                    "ground_truth": test_case["ground_truth"],
                    "error": str(e)
                })

        logger.info("Response generation completed", extra={"total_responses": len(responses)})
        return responses

    def prepare_ragas_dataset(self, responses: List[Dict[str, Any]]) -> Dataset:
        """Prepare dataset in RAGAS format"""
        try:
            # Filter out error responses
            valid_responses = [r for r in responses if "error" not in r]

            if not valid_responses:
                raise ValueError("No valid responses to evaluate")

            # Create RAGAS dataset
            ragas_data = {
                "question": [r["question"] for r in valid_responses],
                "answer": [r["answer"] for r in valid_responses],
                "contexts": [r["contexts"] for r in valid_responses],
                "ground_truth": [r["ground_truth"] for r in valid_responses]
            }

            dataset = Dataset.from_dict(ragas_data)

            logger.info("RAGAS dataset prepared", extra={
                "valid_responses": len(valid_responses),
                "total_responses": len(responses)
            })

            return dataset

        except Exception as e:
            logger.error("Failed to prepare RAGAS dataset", extra={"error": str(e)})
            raise

    async def evaluate_responses(self, dataset: Dataset) -> Dict[str, Any]:
        """Evaluate responses using RAGAS metrics"""
        try:
            logger.info("Starting RAGAS evaluation", extra={"dataset_size": len(dataset)})

            # Run RAGAS evaluation
            results = evaluate(
                dataset=dataset,
                metrics=self.metrics,
            )

            # Convert results to dictionary
            evaluation_results = {
                "overall_scores": dict(results),
                "individual_scores": {},
                "summary": {
                    "total_questions": len(dataset),
                    "avg_faithfulness": results.get("faithfulness", 0),
                    "avg_answer_relevancy": results.get("answer_relevancy", 0),
                    "avg_context_precision": results.get("context_precision", 0),
                    "avg_context_recall": results.get("context_recall", 0),
                    "avg_answer_correctness": results.get("answer_correctness", 0),
                    "avg_answer_similarity": results.get("answer_similarity", 0)
                }
            }

            # Calculate overall score
            metrics_scores = [
                results.get("faithfulness", 0),
                results.get("answer_relevancy", 0),
                results.get("context_precision", 0),
                results.get("context_recall", 0),
                results.get("answer_correctness", 0),
                results.get("answer_similarity", 0)
            ]
            evaluation_results["summary"]["overall_score"] = sum(metrics_scores) / len(metrics_scores)

            logger.info("RAGAS evaluation completed", extra={
                "overall_score": evaluation_results["summary"]["overall_score"],
                "faithfulness": evaluation_results["summary"]["avg_faithfulness"],
                "answer_relevancy": evaluation_results["summary"]["avg_answer_relevancy"]
            })

            return evaluation_results

        except Exception as e:
            logger.error("RAGAS evaluation failed", extra={"error": str(e)})
            raise

    def save_evaluation_results(self, results: Dict[str, Any], responses: List[Dict[str, Any]],
                              output_path: str = None):
        """Save evaluation results to file with unique timestamp"""
        try:
            # Generate unique timestamp-based filename if no path provided
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"output/ragas_evaluation_{timestamp}.json"

            # Prepare comprehensive results
            full_results = {
                "evaluation_summary": results,
                "test_responses": responses,
                "metadata": {
                    "model": settings.openai_model,
                    "embedding_model": settings.embedding_model,
                    "retrieval_top_k": settings.retrieval_top_k,
                    "environment": settings.environment,
                    "timestamp": datetime.now().isoformat(),
                    "evaluation_id": datetime.now().strftime("%Y%m%d_%H%M%S")
                }
            }

            # Save to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(full_results, f, indent=2, default=str)

            logger.info("Evaluation results saved", extra={"output_path": str(output_file)})

            # Also save as CSV for easier analysis
            csv_path = output_file.with_suffix('.csv')
            df = pd.DataFrame(responses)
            df.to_csv(csv_path, index=False)

            logger.info("Results also saved as CSV", extra={"csv_path": str(csv_path)})

            return {
                "json_path": str(output_file),
                "csv_path": str(csv_path)
            }

        except Exception as e:
            logger.error("Failed to save evaluation results", extra={"error": str(e)})
            raise

    async def run_full_evaluation(self, dataset_path: Optional[str] = None) -> Dict[str, Any]:
        """Run complete RAGAS evaluation pipeline"""
        try:
            logger.info("Starting full RAGAS evaluation pipeline")

            # Load test dataset
            test_cases = self.load_test_dataset(dataset_path)

            # Generate responses
            responses = await self.generate_responses(test_cases)

            # Prepare RAGAS dataset
            ragas_dataset = self.prepare_ragas_dataset(responses)

            # Run evaluation
            evaluation_results = await self.evaluate_responses(ragas_dataset)

            # Save results
            file_paths = self.save_evaluation_results(evaluation_results, responses)

            logger.info("Full RAGAS evaluation completed successfully", extra={
                "overall_score": evaluation_results["summary"]["overall_score"],
                "json_file": file_paths["json_path"],
                "csv_file": file_paths["csv_path"]
            })

            # Add file paths to results
            evaluation_results["file_paths"] = file_paths

            return evaluation_results

        except Exception as e:
            logger.error("Full RAGAS evaluation failed", extra={"error": str(e)})
            raise
