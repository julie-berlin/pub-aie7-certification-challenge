#!/usr/bin/env python3
"""
Quick retrieval comparison for certification - focus on getting results fast
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import sys

# Set environment
os.environ["QDRANT_URL"] = "http://localhost:6333"

# Add project root to path
project_root = Path(__file__).parent.parent.parent  
sys.path.append(str(project_root))

from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall, 
    faithfulness,
    answer_relevancy
)
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from qdrant_client import QdrantClient

from api.app.services.ethics_assessment_service import EthicsAssessmentService
from api.app.core.settings import settings

class QuickRetrieverComparison:
    """Quick RAGAS comparison focusing on core metrics"""
    
    def __init__(self):
        self.client = QdrantClient(url="http://localhost:6333", prefer_grpc=False, check_compatibility=False)
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        self.assessment_service = EthicsAssessmentService()
        
        # Fast RAGAS setup
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=settings.openai_api_key,
            timeout=30
        )
    
    def load_dataset(self):
        """Load test scenarios"""
        dataset_file = project_root / "eval/fixtures/test_dataset_markdown.json"
        with open(dataset_file, 'r') as f:
            return json.load(f)
    
    def search_similarity(self, query: str, k: int = 5) -> List[Document]:
        """Similarity search"""
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
    
    def search_mmr(self, query: str, k: int = 5) -> List[Document]:
        """Simple MMR approximation"""
        fetch_k = k * 2
        query_vector = self.embeddings.embed_query(query)
        results = self.client.search(
            collection_name="ethics_knowledge_index", 
            query_vector=query_vector,
            limit=fetch_k
        )
        if not results:
            return []
        
        # Simple diversity selection - take every other result
        selected = []
        for i, result in enumerate(results):
            if len(selected) >= k:
                break
            if i == 0 or i % 2 == 1:  # Take first and every odd result for diversity
                selected.append(Document(
                    page_content=result.payload['page_content'],
                    metadata=result.payload.get('metadata', {})
                ))
        return selected[:k]
    
    def evaluate_strategy(self, strategy_name: str, search_func, scenarios: List[Dict]) -> Dict:
        """Evaluate one strategy"""
        print(f"\n🔍 Evaluating {strategy_name.upper()}...")
        
        questions = []
        contexts = []
        ground_truths = []
        answers = []
        
        for scenario in scenarios:
            try:
                # Get documents
                docs = search_func(scenario['question'])
                context = [doc.page_content for doc in docs]
                
                # Simple answer generation  
                answer = f"Based on federal ethics regulations, this situation involves: {' '.join(context[:1])[:150]}..."
                
                questions.append(scenario['question'])
                contexts.append(context)
                ground_truths.append(scenario['ground_truth'])
                answers.append(answer)
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                continue
        
        if not questions:
            return {"strategy": strategy_name, "error": "No retrievals"}
        
        # RAGAS evaluation
        dataset = Dataset.from_dict({
            "question": questions,
            "contexts": contexts, 
            "answer": answers,
            "ground_truth": ground_truths
        })
        
        metrics = [context_precision, context_recall, faithfulness, answer_relevancy]
        
        try:
            print(f"  🚀 Running RAGAS on {len(questions)} scenarios...")
            results = evaluate(dataset=dataset, metrics=metrics, llm=self.llm, embeddings=self.embeddings)
            scores = dict(results)
            print(f"  ✅ {strategy_name} complete! Scores: {scores}")
            return {"strategy": strategy_name, "dataset_size": len(questions), "scores": scores}
        except Exception as e:
            print(f"  ❌ RAGAS failed: {e}")
            return {"strategy": strategy_name, "error": str(e)}
    
    def run_comparison(self):
        """Run quick comparison"""
        print("🚀 Quick Retrieval Strategy Comparison")
        print("=" * 50)
        
        scenarios = self.load_dataset()
        print(f"📊 {len(scenarios)} test scenarios loaded")
        
        results = {}
        
        # Test similarity
        results["similarity"] = self.evaluate_strategy("similarity", self.search_similarity, scenarios)
        
        # Test MMR
        results["mmr"] = self.evaluate_strategy("mmr", self.search_mmr, scenarios)
        
        # Save results immediately
        self.save_results(results)
        return results
    
    def save_results(self, results: Dict):
        """Save results"""
        output_dir = project_root / "eval/output" 
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON file
        json_file = output_dir / f"quick_retriever_comparison_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "results": results
            }, f, indent=2)
        
        # CSV file
        csv_data = []
        for strategy, result in results.items():
            if "scores" in result:
                row = {"strategy": strategy, "dataset_size": result["dataset_size"]}
                row.update(result["scores"])
                csv_data.append(row)
        
        if csv_data:
            csv_file = output_dir / f"quick_retriever_comparison_{timestamp}.csv"
            pd.DataFrame(csv_data).to_csv(csv_file, index=False)
            print(f"\n📊 Results saved:")
            print(f"   JSON: {json_file}")
            print(f"   CSV: {csv_file}")
            
            # Print summary
            print(f"\n📈 COMPARISON SUMMARY:")
            df = pd.DataFrame(csv_data)
            print(df.to_string(index=False, float_format='{:.4f}'.format))
        else:
            print(f"\n💾 Results saved to: {json_file}")

if __name__ == "__main__":
    evaluator = QuickRetrieverComparison()
    evaluator.run_comparison()