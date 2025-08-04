#!/usr/bin/env python3

import os
from qdrant_client import QdrantClient
from langchain_openai.embeddings import OpenAIEmbeddings
from api.app.core.settings import settings

print("🔍 Testing direct Qdrant connection...")

# Initialize client
client = QdrantClient(url="http://localhost:6333", prefer_grpc=False, check_compatibility=False)

# Get collection info
collection_info = client.get_collection("ethics_knowledge_index")
print(f"Collection vectors: {collection_info.vectors_count}")

# Test with embeddings
embeddings = OpenAIEmbeddings(
    model=settings.embedding_model,
    openai_api_key=settings.openai_api_key
)

query = "Can I accept a gift worth $25 from a contractor?"
print(f"Query: {query}")

# Get query embedding
query_vector = embeddings.embed_query(query)
print(f"Query vector dimension: {len(query_vector)}")

# Search directly
search_result = client.search(
    collection_name="ethics_knowledge_index",
    query_vector=query_vector,
    limit=5
)

print(f"Direct search results: {len(search_result)}")
if search_result:
    for i, result in enumerate(search_result):
        print(f"  {i+1}. Score: {result.score:.4f}")
        print(f"     Content: {result.payload['page_content'][:100]}...")
        print()
        
print("✅ Direct Qdrant search working!")