#!/usr/bin/env python3
"""
Debug RAGAS evaluation to see actual error
"""

import os
import json
os.environ["QDRANT_URL"] = "http://localhost:6333"

from ragas import evaluate
from ragas.metrics import context_precision, context_recall
from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from api.app.core.settings import settings

# Simple test case
questions = ["Can I accept a gift worth $25 from a contractor?"]
contexts = [["Federal employees are prohibited from accepting gifts over $20 from contractors."]]
ground_truths = ["No, federal employees cannot accept gifts over $20 from contractors."]
answers = ["No, you cannot accept a gift worth $25 from a contractor as it exceeds the $20 limit."]

# Create dataset
dataset = Dataset.from_dict({
    "question": questions,
    "contexts": contexts,
    "answer": answers,
    "ground_truth": ground_truths
})

print("Dataset created:", dataset)

# Initialize models
llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.openai_api_key)
embeddings = OpenAIEmbeddings(model=settings.embedding_model, openai_api_key=settings.openai_api_key)

print("Models initialized")

# Try evaluation
try:
    print("Starting evaluation...")
    results = evaluate(
        dataset=dataset,
        metrics=[context_precision, context_recall],
        llm=llm,
        embeddings=embeddings
    )
    print("Results object:", results)
    print("Results type:", type(results))
    print("Results attributes:", dir(results))
    
    # Try different ways to access results
    try:
        print("Results as dict:", dict(results))
    except Exception as e:
        print(f"dict() error: {e}")
    
    try:
        print("Results._scores_dict:", results._scores_dict)
    except Exception as e:
        print(f"_scores_dict error: {e}")
        
    try:
        print("Results to_pandas:", results.to_pandas())
    except Exception as e:
        print(f"to_pandas error: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()