#!/usr/bin/env python3
"""
Initialize vector store with documents and test retrieval strategies
"""

from api.app.services.document_loader_service import DocumentLoaderService
from api.app.services.vector_store_service import VectorStoreService
from api.app.services.advanced_retriever_service import AdvancedRetrieverService
from api.app.core.settings import settings

def initialize_and_test():
    print("🚀 Initializing vector store with documents...")
    
    # Initialize services
    doc_loader = DocumentLoaderService()
    vector_store = VectorStoreService()
    
    # Load documents
    print("📚 Loading ethics documents...")
    documents = doc_loader.load_ethics_documents()
    print(f"   Loaded {len(documents)} base documents")
    
    # Split documents
    print("✂️ Splitting documents into chunks...")
    chunks = doc_loader.split_documents(documents)
    print(f"   Created {len(chunks)} chunks")
    
    # Initialize client and create collection
    print("🗄️ Initializing vector store...")
    vector_store.initialize_client()
    
    # Use default collection name
    collection_name = settings.collection_name
    print(f"   Using collection: {collection_name}")
    
    # Create collection and index documents
    vector_store.create_collection(collection_name)
    success = vector_store.index_documents(chunks, collection_name)
    
    if success:
        print(f"✅ Successfully indexed {len(chunks)} documents in collection '{collection_name}'")
    else:
        print("❌ Failed to index documents")
        return
    
    # Test retrieval strategies
    print("\n🔍 Testing retrieval strategies...")
    advanced_retriever = AdvancedRetrieverService(vector_store)
    
    test_query = "Can I accept a gift worth $25 from a contractor?"
    
    # Test similarity search
    print("   Testing similarity search...")
    similarity_docs = advanced_retriever.retrieve_documents(
        query=test_query,
        strategy="similarity",
        top_k=3
    )
    print(f"   ✅ Similarity search: {len(similarity_docs)} documents retrieved")
    
    # Test MMR
    print("   Testing MMR...")
    mmr_docs = advanced_retriever.retrieve_documents(
        query=test_query,
        strategy="mmr",
        top_k=3
    )
    print(f"   ✅ MMR search: {len(mmr_docs)} documents retrieved")
    
    # Show sample results
    if similarity_docs:
        print(f"\n📄 Sample similarity result:")
        print(f"   {similarity_docs[0].page_content[:200]}...")
    
    if mmr_docs:
        print(f"\n📄 Sample MMR result:")
        print(f"   {mmr_docs[0].page_content[:200]}...")
    
    print("\n✅ Vector store initialization and retrieval test complete!")
    print("🚀 Ready to run RAGAS evaluation!")

if __name__ == "__main__":
    initialize_and_test()