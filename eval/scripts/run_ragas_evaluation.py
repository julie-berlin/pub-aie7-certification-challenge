#!/usr/bin/env python3
"""
RAGAS Evaluation Script for Federal Ethics Chatbot

This script runs a comprehensive evaluation of the ethics chatbot using RAGAS metrics.
It generates responses for test cases and evaluates them for:
- Faithfulness (answer grounded in context)
- Answer Relevancy (relevance to question) 
- Context Precision (precision of retrieved context)
- Context Recall (recall of retrieved context)
- Answer Correctness (correctness vs ground truth)
- Answer Similarity (similarity to ground truth)
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root.parent / "api"))

from api.app.core.logging_config import configure_logging, get_logger
from ragas_evaluation_service import RAGASEvaluationService


async def main():
    """Run RAGAS evaluation"""
    # Configure logging
    configure_logging()
    logger = get_logger("ragas_evaluation_script")
    
    print("🧪 RAGAS Evaluation for Federal Ethics Chatbot")
    print("=" * 60)
    
    try:
        # Initialize evaluation service
        print("🔧 Initializing RAGAS evaluation service...")
        evaluation_service = RAGASEvaluationService()
        
        # Run full evaluation
        print("🚀 Starting comprehensive evaluation...")
        print("⏱️  This may take several minutes depending on the dataset size...")
        
        results = await evaluation_service.run_full_evaluation()
        
        # Display results
        print("\n✅ Evaluation completed successfully!")
        print("=" * 60)
        print("📊 RAGAS EVALUATION RESULTS")
        print("=" * 60)
        
        summary = results["summary"]
        print(f"📋 Total Questions Evaluated: {summary['total_questions']}")
        print(f"🎯 Overall Score: {summary['overall_score']:.3f}")
        print()
        
        print("📈 Individual Metrics:")
        print(f"   🔍 Faithfulness:        {summary['avg_faithfulness']:.3f}")
        print(f"   🎯 Answer Relevancy:    {summary['avg_answer_relevancy']:.3f}")
        print(f"   📊 Context Precision:   {summary['avg_context_precision']:.3f}")
        print(f"   📈 Context Recall:      {summary['avg_context_recall']:.3f}")
        print(f"   ✅ Answer Correctness:  {summary['avg_answer_correctness']:.3f}")
        print(f"   🔗 Answer Similarity:   {summary['avg_answer_similarity']:.3f}")
        print()
        
        # Performance interpretation
        overall_score = summary['overall_score']
        if overall_score >= 0.8:
            performance = "Excellent 🌟"
        elif overall_score >= 0.7:
            performance = "Good 👍"
        elif overall_score >= 0.6:
            performance = "Fair 👌"
        elif overall_score >= 0.5:
            performance = "Needs Improvement 🔧"
        else:
            performance = "Poor - Requires Attention ⚠️"
        
        print(f"🏆 Overall Performance: {performance}")
        print()
        
        # Key insights
        print("🔍 Key Insights:")
        if summary['avg_faithfulness'] < 0.7:
            print("   ⚠️  Low faithfulness - responses may not be well-grounded in retrieved context")
        if summary['avg_context_precision'] < 0.6:
            print("   ⚠️  Low context precision - retrieval may be returning irrelevant documents")
        if summary['avg_context_recall'] < 0.6:
            print("   ⚠️  Low context recall - retrieval may be missing relevant information")
        if summary['avg_answer_correctness'] < 0.7:
            print("   ⚠️  Low answer correctness - responses may not align well with expected answers")
        
        if (summary['avg_faithfulness'] >= 0.7 and 
            summary['avg_context_precision'] >= 0.6 and 
            summary['avg_answer_correctness'] >= 0.7):
            print("   ✅ Strong performance across key metrics!")
        
        print()
        print("📁 Results saved to:")
        if "file_paths" in results:
            print(f"   📄 JSON: eval/{results['file_paths']['json_path']}")
            print(f"   📊 CSV:  eval/{results['file_paths']['csv_path']}")
        else:
            print("   📄 JSON: eval/output/ragas_evaluation_[timestamp].json")
            print("   📊 CSV:  eval/output/ragas_evaluation_[timestamp].csv")
        print()
        
        # Recommendations
        print("💡 Recommendations:")
        if summary['avg_context_precision'] < 0.7:
            print("   🔧 Consider improving retrieval with better chunk sizing or embedding model")
        if summary['avg_faithfulness'] < 0.7:
            print("   🔧 Consider improving prompts to better ground responses in context")
        if summary['avg_answer_correctness'] < 0.7:
            print("   🔧 Consider fine-tuning responses or improving domain knowledge")
        
        print("\n🎉 RAGAS evaluation completed successfully!")
        
        return results
        
    except Exception as e:
        logger.error("RAGAS evaluation failed", extra={"error": str(e)})
        print(f"\n❌ Evaluation failed: {e}")
        print("💡 Make sure:")
        print("   - OpenAI API key is configured")
        print("   - Test dataset exists in data/test_dataset.json")
        print("   - All dependencies are installed")
        return None


def print_usage():
    """Print usage information"""
    print("RAGAS Evaluation Script")
    print("=" * 30)
    print("Usage: python3 scripts/run_ragas_evaluation.py")
    print()
    print("This script evaluates the Federal Ethics Chatbot using RAGAS metrics.")
    print("Make sure you have:")
    print("1. OpenAI API key configured in environment")
    print("2. Test dataset in data/test_dataset.json")
    print("3. All dependencies installed (uv sync)")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print_usage()
        sys.exit(0)
    
    # Run evaluation
    asyncio.run(main())