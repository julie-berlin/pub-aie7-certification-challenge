#!/usr/bin/env python3

import os
# Set environment variables for local connection to Docker Qdrant
os.environ["QDRANT_URL"] = "http://localhost:6333"

from api.app.services.vector_store_service import VectorStoreService
from api.app.services.advanced_retriever_service import AdvancedRetrieverService
from api.app.core.settings import settings

print("🚀 Testing retrieval with existing vector store...")
print(f"Qdrant URL: {settings.qdrant_url}")

# Initialize vector store service
vs = VectorStoreService()
vs.initialize_client()

# Test basic retrieval first
query = "Can I accept a gift worth $25 from a contractor?"
print(f"\n🔍 Testing basic similarity search: {query}")

try:
    results = vs.similarity_search(query, k=5, collection_name="ethics_knowledge_index")
    print(f"✅ Retrieved {len(results)} documents")
    
    if results:
        print(f"\n📄 Sample result:")
        print(f"   {results[0].page_content[:200]}...")
        
        # Test advanced retrieval strategies
        print(f"\n🔍 Testing advanced retrieval strategies...")
        advanced_retriever = AdvancedRetrieverService(vs)
        
        print(f"   Testing similarity strategy...")
        similarity_docs = advanced_retriever.retrieve_documents(
            query=query, 
            strategy="similarity", 
            collection_name="ethics_knowledge_index",
            top_k=3
        )
        print(f"   ✅ Similarity: {len(similarity_docs)} docs")
        
        print(f"   Testing MMR strategy...")
        mmr_docs = advanced_retriever.retrieve_documents(
            query=query, 
            strategy="mmr", 
            collection_name="ethics_knowledge_index",
            top_k=3
        )
        print(f"   ✅ MMR: {len(mmr_docs)} docs")
        
        # Show comparison
        if similarity_docs and mmr_docs:
            print(f"\n📊 Strategy Comparison:")
            print(f"   Similarity first result: {similarity_docs[0].page_content[:100]}...")
            print(f"   MMR first result: {mmr_docs[0].page_content[:100]}...")
            
        print("\n✅ Retrieval strategies working! Ready for RAGAS evaluation!")
        
    else:
        print("❌ No documents retrieved")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()