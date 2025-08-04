#!/usr/bin/env python3

# Initialize documents first, then test retrieval
from api.app.services.document_loader_service import DocumentLoaderService
from api.app.services.vector_store_service import VectorStoreService
from api.app.core.settings import settings

print("🚀 Initializing vector store with documents...")

# Load and split documents
doc_loader = DocumentLoaderService()
documents = doc_loader.load_ethics_documents()
print(f"📚 Loaded {len(documents)} documents")

chunks = doc_loader.split_documents(documents)
print(f"✂️ Created {len(chunks)} chunks")

# Initialize vector store
vs = VectorStoreService()
vs.initialize_client()

# Index documents
print("🗄️ Indexing documents...")
success = vs.index_documents(chunks, settings.collection_name)
print(f"Indexing success: {success}")

if success:
    # Test retrieval
    query = "Can I accept a gift worth $25 from a contractor?"
    print(f"\n🔍 Testing retrieval with query: {query}")
    
    results = vs.similarity_search(query, k=5)
    print(f"✅ Retrieved {len(results)} documents")
    
    if results:
        print(f"\n📄 Sample result:")
        print(f"   {results[0].page_content[:200]}...")
        
        # Now test advanced retrieval strategies
        from api.app.services.advanced_retriever_service import AdvancedRetrieverService
        advanced_retriever = AdvancedRetrieverService(vs)
        
        print(f"\n🔍 Testing similarity strategy...")
        similarity_docs = advanced_retriever.retrieve_documents(query, "similarity", top_k=3)
        print(f"   Similarity: {len(similarity_docs)} docs")
        
        print(f"\n🔍 Testing MMR strategy...")
        mmr_docs = advanced_retriever.retrieve_documents(query, "mmr", top_k=3)
        print(f"   MMR: {len(mmr_docs)} docs")
        
        print("\n✅ Ready for RAGAS evaluation!")
else:
    print("❌ Failed to index documents")