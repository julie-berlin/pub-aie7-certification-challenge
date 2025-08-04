#!/usr/bin/env python3
"""
RAGAS-based evaluation comparing 3 retrieval strategies:
- Similarity Search (baseline)
- Cohere Rerank 
- MMR (Maximum Marginal Relevance)
"""

import asyncio
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path for imports
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall, 
    ContextRelevance,
    faithfulness,
    answer_relevancy
)
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Import our services
from api.app.services.vector_store_service import VectorStoreService
from api.app.services.advanced_retriever_service import AdvancedRetrieverService
from api.app.services.ethics_assessment_service import EthicsAssessmentService
from api.app.core.settings import settings


class RetrieverRAGASEvaluator:
    """Evaluate retrieval strategies using RAGAS metrics"""
    
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.advanced_retriever = AdvancedRetrieverService(self.vector_store_service)
        self.assessment_service = EthicsAssessmentService()
        
        # Initialize vector store
        self.vector_store_service.initialize_client()
        
        # RAGAS models
        self.llm = ChatOpenAI(
            model="gpt-4o", 
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
    
    def load_golden_dataset(self, dataset_path: str = "eval/fixtures/test_dataset_markdown.json") -> List[Dict]:
        """Load the golden dataset for evaluation"""
        dataset_file = project_root / dataset_path
        if not dataset_file.exists():
            raise FileNotFoundError(f"Golden dataset not found at {dataset_file}")
        
        with open(dataset_file, 'r') as f:
            data = json.load(f)
            
        print(f"📊 Loaded {len(data)} test scenarios from {dataset_file}")
        return data
    
    def evaluate_retriever_strategy(
        self, 
        strategy: str,
        test_scenarios: List[Dict],
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Evaluate a single retrieval strategy using RAGAS"""
        
        print(f"\n🔍 Evaluating {strategy.upper()} retrieval strategy...")
        
        # Prepare data for RAGAS evaluation
        questions = []
        contexts = []
        ground_truths = []
        answers = []
        
        for i, scenario in enumerate(test_scenarios):
            print(f"  Processing scenario {i+1}/{len(test_scenarios)}: {scenario['question'][:80]}...")
            
            try:
                # Retrieve documents using the strategy
                retrieved_docs = self.advanced_retriever.retrieve_documents(
                    query=scenario['question'],
                    strategy=strategy,
                    top_k=top_k
                )
                
                # Prepare context from retrieved documents
                context = [doc.page_content for doc in retrieved_docs]
                
                # Generate answer using retrieved context (simplified for RAGAS)
                federal_context = "\n\n".join(context)
                
                answer = self.assessment_service.assess_ethics_scenario(
                    question=scenario['question'],
                    search_plan="RAGAS evaluation - no web search",
                    user_context=scenario.get('user_context', {}),
                    federal_context=federal_context,
                    general_results="",
                    penalty_results="",
                    guidance_results=""
                )
                
                # Collect data for RAGAS
                questions.append(scenario['question'])
                contexts.append(context)
                ground_truths.append(scenario['ground_truth'])
                answers.append(answer)
                
            except Exception as e:
                print(f"    ❌ Error processing scenario {i+1}: {e}")
                continue
        
        # Create RAGAS dataset
        ragas_dataset = Dataset.from_dict({
            "question": questions,
            "contexts": contexts,
            "answer": answers,
            "ground_truth": ground_truths
        })
        
        print(f"  ✅ Created RAGAS dataset with {len(questions)} scenarios")
        
        # Run RAGAS evaluation
        print(f"  🚀 Running RAGAS evaluation...")
        
        # Select metrics for retrieval evaluation
        metrics = [
            context_precision,       # How relevant are retrieved contexts
            context_recall,          # How much of ground truth is covered
            ContextRelevance(),      # How relevant contexts are to question
            faithfulness,            # How faithful is answer to context
            answer_relevancy         # How relevant is answer to question
        ]
        
        try:
            results = evaluate(
                dataset=ragas_dataset,
                metrics=metrics,
                llm=self.llm,
                embeddings=self.embeddings
            )
            
            print(f"  ✅ RAGAS evaluation completed for {strategy}")
            
            return {
                "strategy": strategy,
                "dataset_size": len(questions),
                "scores": dict(results),
                "ragas_dataset": ragas_dataset
            }
            
        except Exception as e:
            print(f"  ❌ Error in RAGAS evaluation for {strategy}: {e}")
            return {
                "strategy": strategy,
                "dataset_size": len(questions),
                "error": str(e),
                "ragas_dataset": ragas_dataset
            }
    
    def compare_strategies(
        self,
        strategies: List[str] = ["similarity", "mmr"],
        top_k: int = 5,
        dataset_path: str = "eval/fixtures/test_dataset_markdown.json"
    ) -> Dict[str, Any]:
        """Compare multiple retrieval strategies using RAGAS"""
        
        print("🚀 Starting RAGAS-based retrieval strategy comparison")
        print(f"📈 Strategies: {strategies}")
        print(f"🔢 Top-K: {top_k}")
        print("-" * 80)
        
        # Load test dataset
        test_scenarios = self.load_golden_dataset(dataset_path)
        
        # Evaluate each strategy
        results = {}
        for strategy in strategies:
            results[strategy] = self.evaluate_retriever_strategy(
                strategy=strategy,
                test_scenarios=test_scenarios,
                top_k=top_k
            )
        
        # Create comparison summary
        comparison = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "strategies_compared": strategies,
            "top_k": top_k,
            "dataset_size": len(test_scenarios),
            "results": results
        }
        
        return comparison
    
    def save_results(self, comparison_results: Dict[str, Any], output_dir: str = "eval/output"):
        """Save comparison results to files"""
        
        output_path = project_root / output_dir
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full results as JSON
        json_file = output_path / f"retriever_comparison_{timestamp}.json"
        
        # Remove ragas_dataset objects for JSON serialization
        json_results = comparison_results.copy()
        for strategy in json_results.get("results", {}):
            if "ragas_dataset" in json_results["results"][strategy]:
                del json_results["results"][strategy]["ragas_dataset"]
        
        with open(json_file, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        # Create summary CSV
        csv_data = []
        for strategy, result in comparison_results.get("results", {}).items():
            if "scores" in result:
                row = {"strategy": strategy}
                row.update(result["scores"])
                csv_data.append(row)
        
        csv_file = None
        if csv_data:
            csv_file = output_path / f"retriever_comparison_{timestamp}.csv"
            pd.DataFrame(csv_data).to_csv(csv_file, index=False)
            print(f"📊 Summary saved to {csv_file}")
        
        print(f"💾 Full results saved to {json_file}")
        return json_file, csv_file
    
    def print_comparison_summary(self, comparison_results: Dict[str, Any]):
        """Print a formatted summary of the comparison"""
        
        print("\n" + "="*80)
        print("🏆 RAGAS RETRIEVAL STRATEGY COMPARISON RESULTS")
        print("="*80)
        
        results = comparison_results.get("results", {})
        
        # Print individual strategy results
        for strategy, result in results.items():
            print(f"\n📈 {strategy.upper().replace('_', ' ')} STRATEGY:")
            print("-" * 50)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            if "scores" in result:
                scores = result["scores"]
                print(f"📊 Dataset Size: {result.get('dataset_size', 'N/A')}")
                print("\nRAGAS Metrics:")
                
                for metric, score in scores.items():
                    if isinstance(score, (int, float)):
                        print(f"  • {metric}: {score:.4f}")
                    else:
                        print(f"  • {metric}: {score}")
        
        # Determine winner for each metric
        print(f"\n🥇 METRIC WINNERS:")
        print("-" * 30)
        
        all_metrics = set()
        for result in results.values():
            if "scores" in result:
                all_metrics.update(result["scores"].keys())
        
        for metric in all_metrics:
            metric_scores = {}
            for strategy, result in results.items():
                if "scores" in result and metric in result["scores"]:
                    score = result["scores"][metric]
                    if isinstance(score, (int, float)):
                        metric_scores[strategy] = score
            
            if metric_scores:
                winner = max(metric_scores.items(), key=lambda x: x[1])
                print(f"  • {metric}: {winner[0].replace('_', ' ').title()} ({winner[1]:.4f})")
        
        # Overall recommendation
        print(f"\n💡 STRATEGY COMPARISON:")
        print("-" * 30)
        print("• Similarity: Simple baseline, fastest")
        print("• Cohere Rerank: Advanced relevance scoring")  
        print("• MMR: Balances relevance with diversity")


async def main():
    """Main evaluation function"""
    
    evaluator = RetrieverRAGASEvaluator()
    
    # Run comparison
    comparison_results = evaluator.compare_strategies(
        strategies=["similarity", "mmr"],
        top_k=5
    )
    
    # Save and display results
    json_file, csv_file = evaluator.save_results(comparison_results)
    evaluator.print_comparison_summary(comparison_results)
    
    print(f"\n✅ Evaluation complete! Results saved to:")
    print(f"   📄 {json_file}")
    if csv_file:
        print(f"   📊 {csv_file}")


if __name__ == "__main__":
    asyncio.run(main())