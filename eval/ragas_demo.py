#!/usr/bin/env python3
"""
RAGAS Evaluation Demo

This script demonstrates how to use the RAGAS evaluation system
for the Federal Ethics Chatbot.
"""

import sys
import json
from pathlib import Path

# Add api to path
project_root = Path(__file__).parent
sys.path.append(str(project_root.parent / "api"))

def print_sample_results():
    """Print sample RAGAS evaluation results"""
    print("🎯 RAGAS Evaluation Demo")
    print("=" * 50)
    
    # Sample results (what you might expect to see)
    sample_results = {
        "summary": {
            "total_questions": 12,
            "overall_score": 0.742,
            "avg_faithfulness": 0.823,
            "avg_answer_relevancy": 0.789,
            "avg_context_precision": 0.654,
            "avg_context_recall": 0.712,
            "avg_answer_correctness": 0.778,
            "avg_answer_similarity": 0.765
        }
    }
    
    print("📊 Sample RAGAS Results:")
    print("-" * 30)
    summary = sample_results["summary"]
    print(f"📋 Total Questions: {summary['total_questions']}")
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
    
    print(f"🏆 Performance: {performance}")
    print()
    
    print("🔍 Analysis:")
    if summary['avg_context_precision'] < 0.7:
        print("   ⚠️  Context precision could be improved - consider better retrieval")
    if summary['avg_faithfulness'] > 0.8:
        print("   ✅ Strong faithfulness - responses well-grounded in context")
    if summary['avg_answer_correctness'] > 0.75:
        print("   ✅ Good answer correctness - responses align with expectations")
    
    print()

def show_test_dataset_sample():
    """Show sample from test dataset"""
    print("📋 Test Dataset Sample")
    print("=" * 30)
    
    sample_test_case = {
        "question": "Can I accept a gift worth $25 from a contractor my agency works with?",
        "user_context": {
            "role": "federal_employee",
            "agency": "GSA", 
            "seniority": "GS-12"
        },
        "ground_truth": "No, you cannot accept a gift worth $25 from a contractor your agency works with. Under federal ethics rules, you generally cannot accept gifts from prohibited sources, which includes contractors who do business with your agency.",
        "expected_violations": ["Gift acceptance from prohibited source", "5 CFR 2635.202"],
        "expected_severity": "moderate"
    }
    
    print("❓ Question:")
    print(f"   {sample_test_case['question']}")
    print()
    
    print("👤 User Context:")
    ctx = sample_test_case['user_context']
    print(f"   Role: {ctx['role']}")
    print(f"   Agency: {ctx['agency']}")
    print(f"   Level: {ctx['seniority']}")
    print()
    
    print("✅ Ground Truth:")
    print(f"   {sample_test_case['ground_truth'][:100]}...")
    print()
    
    print("⚖️ Expected Violations:")
    for violation in sample_test_case['expected_violations']:
        print(f"   - {violation}")
    print()
    
    print(f"🚨 Severity: {sample_test_case['expected_severity']}")
    print()

def show_usage_instructions():
    """Show how to run RAGAS evaluation"""
    print("🚀 How to Run RAGAS Evaluation")
    print("=" * 40)
    
    print("1. Prerequisites:")
    print("   ✅ Install dependencies: uv sync")
    print("   ✅ Set OPENAI_API_KEY environment variable")
    print("   ✅ Optionally set TAVILY_API_KEY for web search")
    print()
    
    print("2. Run Evaluation:")
    print("   ```bash")
    print("   python3 eval/scripts/run_ragas_evaluation.py")
    print("   ```")
    print()
    
    print("3. View Results:")
    print("   📄 JSON: eval/output/ragas_evaluation_YYYYMMDD_HHMMSS.json")
    print("   📊 CSV:  eval/output/ragas_evaluation_YYYYMMDD_HHMMSS.csv")
    print("   🕒 Each run creates uniquely timestamped files")
    print()
    
    print("4. Interpret Scores:")
    print("   🌟 0.8-1.0: Excellent")
    print("   👍 0.7-0.8: Good") 
    print("   👌 0.6-0.7: Fair")
    print("   🔧 0.5-0.6: Needs Improvement")
    print("   ⚠️  0.0-0.5: Poor")
    print()

def main():
    """Main demo function"""
    print("🧪 Federal Ethics Chatbot - RAGAS Evaluation Demo")
    print("=" * 60)
    print()
    
    # Show test dataset sample
    show_test_dataset_sample()
    
    # Show sample results
    print_sample_results()
    
    # Show usage instructions
    show_usage_instructions()
    
    print("📚 For more details, see:")
    print("   📖 docs/ragas_evaluation_guide.md")
    print("   🔧 eval/ragas_evaluation_service.py")
    print("   📋 eval/test_dataset.json")
    print()
    print("🎉 Ready to evaluate your Federal Ethics Chatbot!")

if __name__ == "__main__":
    main()