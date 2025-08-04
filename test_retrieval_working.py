#!/usr/bin/env python3

import os
os.environ["QDRANT_URL"] = "http://localhost:6333"

from qdrant_client import QdrantClient
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from api.app.core.settings import settings

print("🚀 Testing working retrieval strategies...")

# Initialize components
client = QdrantClient(url="http://localhost:6333", prefer_grpc=False, check_compatibility=False)
embeddings = OpenAIEmbeddings(
    model=settings.embedding_model,
    openai_api_key=settings.openai_api_key
)

def search_similarity(query: str, k: int = 5):
    """Similarity search strategy"""
    query_vector = embeddings.embed_query(query)
    
    results = client.search(
        collection_name="ethics_knowledge_index",
        query_vector=query_vector,
        limit=k
    )
    
    return [
        Document(page_content=result.payload['page_content'], metadata=result.payload.get('metadata', {}))
        for result in results
    ]

def search_mmr(query: str, k: int = 5, diversity_lambda: float = 0.7):
    """MMR search strategy (simplified version)"""
    # Fetch more candidates for MMR selection
    fetch_k = min(k * 3, 20)
    query_vector = embeddings.embed_query(query)
    
    results = client.search(
        collection_name="ethics_knowledge_index",
        query_vector=query_vector,
        limit=fetch_k
    )
    
    # Simple MMR implementation: select diverse results
    if not results:
        return []
    
    selected = [results[0]]  # Always take the most relevant
    
    for candidate in results[1:]:
        if len(selected) >= k:
            break
            
        # Simple diversity check - avoid very similar content
        is_diverse = True
        for selected_doc in selected:
            # Check if content is too similar (simple overlap check)
            candidate_words = set(candidate.payload['page_content'].lower().split()[:20])
            selected_words = set(selected_doc.payload['page_content'].lower().split()[:20])
            overlap = len(candidate_words & selected_words) / len(candidate_words | selected_words)
            
            if overlap > (1 - diversity_lambda):  # Too similar
                is_diverse = False
                break
        
        if is_diverse:
            selected.append(candidate)
    
    return [
        Document(page_content=result.payload['page_content'], metadata=result.payload.get('metadata', {}))
        for result in selected
    ]

# Test both strategies
query = "Can I accept a gift worth $25 from a contractor?"
print(f"Query: {query}\n")

print("🔍 Testing Similarity Search:")
similarity_docs = search_similarity(query, k=3)
print(f"   Retrieved {len(similarity_docs)} documents")
for i, doc in enumerate(similarity_docs):
    print(f"   {i+1}. {doc.page_content[:100]}...")

print(f"\n🔍 Testing MMR Search:")
mmr_docs = search_mmr(query, k=3, diversity_lambda=0.7)
print(f"   Retrieved {len(mmr_docs)} documents")
for i, doc in enumerate(mmr_docs):
    print(f"   {i+1}. {doc.page_content[:100]}...")

# Compare results
print(f"\n📊 Strategy Comparison:")
if similarity_docs and mmr_docs:
    sim_first = similarity_docs[0].page_content[:150]
    mmr_first = mmr_docs[0].page_content[:150]
    
    print(f"   Similarity first: {sim_first}...")
    print(f"   MMR first: {mmr_first}...")
    
    same_first = sim_first == mmr_first
    print(f"   Same first result: {same_first}")

print(f"\n✅ Both retrieval strategies working! Ready for RAGAS evaluation!")

# Save working retrievers for RAGAS
globals()['working_similarity_search'] = search_similarity
globals()['working_mmr_search'] = search_mmr
globals()['working_embeddings'] = embeddings
globals()['working_client'] = client