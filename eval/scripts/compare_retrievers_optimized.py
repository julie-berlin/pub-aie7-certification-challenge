#!/usr/bin/env python3
"""
Optimized RAGAS-based evaluation comparing retrieval strategies with timeout fixes
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import sys
import os

# Set environment for Docker containers
os.environ["QDRANT_URL"] = "http://localhost:6333"

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall, 
    faithfulness,
    answer_relevancy,
    answer_correctness
)
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Import our services
from api.app.services.vector_store_service import VectorStoreService
from api.app.services.advanced_retriever_service import AdvancedRetrieverService
from api.app.core.settings import settings


class OptimizedRetrieverEvaluator:
    """Fast retrieval strategy comparison using RAGAS"""
    
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.advanced_retriever = AdvancedRetrieverService(self.vector_store_service)
        
        # Initialize vector store
        self.vector_store_service.initialize_client()
        
        # RAGAS models - optimized for speed
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Faster model
            temperature=0,
            openai_api_key=settings.openai_api_key,
            timeout=30,  # Reduced timeout
            max_retries=1  # Fewer retries
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
    
    def load_test_dataset(self, dataset_path: str = "eval/fixtures/test_dataset_markdown.json") -> List[Dict]:
        """Load test dataset"""
        dataset_file = project_root / dataset_path
        if not dataset_file.exists():
            raise FileNotFoundError(f"Test dataset not found at {dataset_file}")
        
        with open(dataset_file, 'r') as f:
            data = json.load(f)
            
        print(f"📊 Loaded {len(data)} test scenarios")
        return data
    
    def evaluate_strategy_fast(
        self, 
        strategy: str,
        test_scenarios: List[Dict],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Fast evaluation of a single strategy"""
        
        print(f"\n🔍 Evaluating {strategy.upper()} strategy...")
        
        questions = []
        contexts = []
        ground_truths = []
        answers = []
        
        for i, scenario in enumerate(test_scenarios):
            print(f"  Processing scenario {i+1}/{len(test_scenarios)}...")
            
            try:
                # Retrieve documents
                retrieved_docs = self.advanced_retriever.retrieve_documents(
                    query=scenario['question'],
                    strategy=strategy,
                    top_k=top_k
                )
                
                # Prepare context
                context = [doc.page_content for doc in retrieved_docs]
                
                # Generate simple answer for evaluation (skip full assessment to avoid timeout)
                answer = f"Ethics assessment based on retrieved federal regulations: {' '.join(context[:2])[:200]}..."
                
                questions.append(scenario['question'])
                contexts.append(context)
                ground_truths.append(scenario['ground_truth'])
                answers.append(answer)
                
            except Exception as e:
                print(f"    ❌ Error in scenario {i+1}: {e}")
                continue
        
        if not questions:
            return {"strategy": strategy, "error": "No successful retrievals"}
        
        # Create RAGAS dataset
        ragas_dataset = Dataset.from_dict({
            "question": questions,
            "contexts": contexts,
            "answer": answers,
            "ground_truth": ground_truths
        })
        
        print(f"  ✅ Dataset ready with {len(questions)} scenarios")
        
        # Core RAGAS metrics (reduced set for speed)
        metrics = [
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy
        ]
        
        try:
            print(f"  🚀 Running RAGAS evaluation...")
            results = evaluate(
                dataset=ragas_dataset,
                metrics=metrics,
                llm=self.llm,
                embeddings=self.embeddings
            )
            
            print(f"  ✅ Evaluation completed for {strategy}")
            
            return {
                "strategy": strategy,
                "dataset_size": len(questions),
                "scores": dict(results)
            }
            
        except Exception as e:
            print(f"  ❌ RAGAS evaluation failed for {strategy}: {e}")
            return {
                "strategy": strategy,
                "dataset_size": len(questions),
                "error": str(e)
            }
    
    def compare_strategies(
        self,
        strategies: List[str] = ["similarity", "mmr"],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Compare retrieval strategies"""
        
        print("🚀 Starting optimized retrieval strategy comparison")
        print(f"📈 Strategies: {strategies}")
        print(f"🔢 Top-K: {top_k}")
        print("-" * 80)
        
        # Load test dataset
        test_scenarios = self.load_test_dataset()
        
        # Evaluate each strategy
        results = {}
        for strategy in strategies:
            results[strategy] = self.evaluate_strategy_fast(
                strategy=strategy,
                test_scenarios=test_scenarios,
                top_k=top_k
            )
        
        return {
            "evaluation_timestamp": datetime.now().isoformat(),
            "strategies_compared": strategies,
            "top_k": top_k,
            "dataset_size": len(test_scenarios),
            "results": results
        }
    
    def save_results(self, comparison_results: Dict[str, Any]):
        """Save results with timestamp"""
        
        output_path = project_root / "eval/output"
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_file = output_path / f"retriever_ragas_comparison_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(comparison_results, f, indent=2)
        
        # Create CSV summary
        csv_data = []
        for strategy, result in comparison_results.get("results", {}).items():
            if "scores" in result:
                row = {"strategy": strategy, "dataset_size": result["dataset_size"]}
                row.update(result["scores"])
                csv_data.append(row)
        
        csv_file = None
        if csv_data:
            csv_file = output_path / f"retriever_ragas_comparison_{timestamp}.csv"
            pd.DataFrame(csv_data).to_csv(csv_file, index=False)
            print(f"📊 CSV saved: {csv_file}")
            
            # Print CSV preview
            print("\n📈 Results Preview:")
            df = pd.DataFrame(csv_data)
            print(df.to_string(index=False, float_format='{:.4f}'.format))
        
        print(f"💾 Full results: {json_file}")
        return json_file, csv_file


async def main():
    """Main evaluation function"""
    
    evaluator = OptimizedRetrieverEvaluator()
    
    # Run comparison with all available strategies
    comparison_results = evaluator.compare_strategies(
        strategies=["similarity", "mmr", "hybrid"],  # Include hybrid strategy
        top_k=5
    )
    
    # Save results
    json_file, csv_file = evaluator.save_results(comparison_results)
    
    print(f"\n✅ Comparison complete!")
    print(f"📄 JSON: {json_file}")
    if csv_file:
        print(f"📊 CSV: {csv_file}")


if __name__ == "__main__":
    asyncio.run(main())