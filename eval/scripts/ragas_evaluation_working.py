#!/usr/bin/env python3
"""
RAGAS evaluation using working retrieval strategies
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Set environment
os.environ["QDRANT_URL"] = "http://localhost:6333"

# Add project root to path
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
from langchain_core.documents import Document
from qdrant_client import QdrantClient

from api.app.services.ethics_assessment_service import EthicsAssessmentService
from api.app.core.settings import settings

class WorkingRetrieverEvaluator:
    """RAGAS evaluation using working direct Qdrant retrieval"""
    
    def __init__(self):
        # Initialize components
        self.client = QdrantClient(url="http://localhost:6333", prefer_grpc=False, check_compatibility=False)
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        self.assessment_service = EthicsAssessmentService()
        
        # RAGAS models
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
    
    def search_similarity(self, query: str, k: int = 5) -> List[Document]:
        """Similarity search strategy"""
        query_vector = self.embeddings.embed_query(query)
        
        results = self.client.search(
            collection_name="ethics_knowledge_index",
            query_vector=query_vector,
            limit=k
        )
        
        return [
            Document(page_content=result.payload['page_content'], metadata=result.payload.get('metadata', {}))
            for result in results
        ]
    
    def search_mmr(self, query: str, k: int = 5, diversity_lambda: float = 0.7) -> List[Document]:
        """MMR search strategy with diversity"""
        fetch_k = min(k * 3, 20)
        query_vector = self.embeddings.embed_query(query)
        
        results = self.client.search(
            collection_name="ethics_knowledge_index",
            query_vector=query_vector,
            limit=fetch_k
        )
        
        if not results:
            return []
        
        selected = [results[0]]  # Most relevant
        
        for candidate in results[1:]:
            if len(selected) >= k:
                break
                
            # Check diversity - avoid very similar content
            is_diverse = True
            for selected_doc in selected:
                candidate_words = set(candidate.payload['page_content'].lower().split()[:30])
                selected_words = set(selected_doc.payload['page_content'].lower().split()[:30])
                if candidate_words and selected_words:
                    overlap = len(candidate_words & selected_words) / len(candidate_words | selected_words)
                    if overlap > (1 - diversity_lambda):
                        is_diverse = False
                        break
            
            if is_diverse:
                selected.append(candidate)
        
        return [
            Document(page_content=result.payload['page_content'], metadata=result.payload.get('metadata', {}))
            for result in selected
        ]
    
    def load_test_dataset(self) -> List[Dict]:
        """Load test dataset"""
        dataset_file = project_root / "eval/fixtures/test_dataset_markdown.json"
        with open(dataset_file, 'r') as f:
            return json.load(f)
    
    def evaluate_strategy(self, strategy_name: str, search_function, test_scenarios: List[Dict]) -> Dict:
        """Evaluate a single retrieval strategy"""
        print(f"\n🔍 Evaluating {strategy_name.upper()} strategy...")
        
        questions = []
        contexts = []
        ground_truths = []
        answers = []
        
        for i, scenario in enumerate(test_scenarios):
            print(f"   Processing scenario {i+1}/{len(test_scenarios)}...")
            
            try:
                # Retrieve documents
                docs = search_function(scenario['question'], k=5)
                context = [doc.page_content for doc in docs]
                
                # Generate answer using retrieved context
                federal_context = "\n\n".join(context)
                answer = self.assessment_service.assess_ethics_scenario(
                    question=scenario['question'],
                    search_plan=f"RAGAS evaluation using {strategy_name}",
                    user_context=scenario.get('user_context', {}),
                    federal_context=federal_context,
                    general_results="",
                    penalty_results="",
                    guidance_results=""
                )
                
                questions.append(scenario['question'])
                contexts.append(context)
                ground_truths.append(scenario['ground_truth'])
                answers.append(answer)
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                continue
        
        if not questions:
            return {"error": "No scenarios processed successfully"}
        
        # Create RAGAS dataset
        ragas_dataset = Dataset.from_dict({
            "question": questions,
            "contexts": contexts,
            "answer": answers,
            "ground_truth": ground_truths
        })
        
        print(f"   🚀 Running RAGAS evaluation on {len(questions)} scenarios...")
        
        # RAGAS metrics
        metrics = [
            context_precision,
            context_recall,
            ContextRelevance(),
            faithfulness,
            answer_relevancy
        ]
        
        try:
            results = evaluate(
                dataset=ragas_dataset,
                metrics=metrics,
                llm=self.llm,
                embeddings=self.embeddings
            )
            
            # Extract scores properly from RAGAS results
            scores = {}
            if hasattr(results, '_scores_dict'):
                for metric, values in results._scores_dict.items():
                    # Take the mean of all values for each metric
                    scores[metric] = sum(values) / len(values) if values else 0.0
            
            print(f"   ✅ {strategy_name} evaluation complete!")
            print(f"       Scores: {scores}")
            
            return {
                "strategy": strategy_name,
                "dataset_size": len(questions),
                "scores": scores
            }
            
        except Exception as e:
            print(f"   ❌ RAGAS evaluation error: {e}")
            return {
                "strategy": strategy_name,
                "dataset_size": len(questions),
                "error": str(e)
            }
    
    def run_comparison(self) -> Dict:
        """Run complete strategy comparison"""
        print("🚀 Starting RAGAS retrieval strategy comparison")
        print("=" * 60)
        
        # Load test data
        test_scenarios = self.load_test_dataset()
        print(f"📊 Loaded {len(test_scenarios)} test scenarios")
        
        # Evaluate strategies
        results = {}
        
        # Similarity search
        results["similarity"] = self.evaluate_strategy(
            "similarity", 
            self.search_similarity, 
            test_scenarios
        )
        
        # MMR search
        results["mmr"] = self.evaluate_strategy(
            "mmr", 
            self.search_mmr, 
            test_scenarios
        )
        
        return {
            "evaluation_timestamp": datetime.now().isoformat(),
            "strategies_compared": ["similarity", "mmr"],
            "dataset_size": len(test_scenarios),
            "results": results
        }
    
    def save_results(self, comparison_results: Dict) -> tuple:
        """Save results to files"""
        output_dir = project_root / "eval/output"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_file = output_dir / f"retriever_ragas_comparison_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(comparison_results, f, indent=2)
        
        # Save CSV summary
        csv_data = []
        for strategy, result in comparison_results.get("results", {}).items():
            if "scores" in result:
                row = {"strategy": strategy, "dataset_size": result.get("dataset_size", 0)}
                row.update(result["scores"])
                csv_data.append(row)
        
        csv_file = None
        if csv_data:
            csv_file = output_dir / f"retriever_ragas_comparison_{timestamp}.csv"
            pd.DataFrame(csv_data).to_csv(csv_file, index=False)
        
        return json_file, csv_file
    
    def print_results(self, comparison_results: Dict):
        """Print formatted results"""
        print("\n" + "=" * 80)
        print("🏆 RAGAS RETRIEVAL STRATEGY COMPARISON RESULTS")
        print("=" * 80)
        
        results = comparison_results.get("results", {})
        
        for strategy, result in results.items():
            print(f"\n📈 {strategy.upper()} STRATEGY:")
            print("-" * 40)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            if "scores" in result:
                print(f"📊 Dataset Size: {result.get('dataset_size', 'N/A')}")
                print("RAGAS Metrics:")
                
                for metric, score in result["scores"].items():
                    if isinstance(score, (int, float)):
                        print(f"  • {metric}: {score:.4f}")
        
        # Show winners
        print(f"\n🥇 METRIC WINNERS:")
        print("-" * 25)
        
        all_metrics = set()
        for result in results.values():
            if "scores" in result:
                all_metrics.update(result["scores"].keys())
        
        for metric in all_metrics:
            scores = {}
            for strategy, result in results.items():
                if "scores" in result and metric in result["scores"]:
                    score = result["scores"][metric]
                    if isinstance(score, (int, float)):
                        scores[strategy] = score
            
            if scores:
                winner = max(scores.items(), key=lambda x: x[1])
                print(f"  • {metric}: {winner[0]} ({winner[1]:.4f})")


def main():
    """Main evaluation function"""
    evaluator = WorkingRetrieverEvaluator()
    
    # Run comparison
    results = evaluator.run_comparison()
    
    # Save and display
    json_file, csv_file = evaluator.save_results(results)
    evaluator.print_results(results)
    
    print(f"\n✅ Evaluation complete!")
    print(f"   📄 Results: {json_file}")
    if csv_file:
        print(f"   📊 Summary: {csv_file}")


if __name__ == "__main__":
    main()