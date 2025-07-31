from typing import List, Optional
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from ..core.settings import settings


class VectorStoreService:
    """Service for managing Qdrant vector database operations"""
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.vector_store: Optional[QdrantVectorStore] = None
        self.embedding_model = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
    
    def initialize_client(self) -> QdrantClient:
        """Initialize Qdrant client connection"""
        try:
            if settings.qdrant_url == "memory":
                self.client = QdrantClient(":memory:")
            else:
                self.client = QdrantClient(url=settings.qdrant_url)
            
            print(f"✅ Connected to Qdrant at {settings.qdrant_url}")
            return self.client
            
        except Exception as e:
            print(f"❌ Failed to connect to Qdrant: {e}")
            raise
    
    def create_collection(self) -> bool:
        """Create ethics knowledge collection if it doesn't exist"""
        try:
            if not self.client:
                self.initialize_client()
            
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if settings.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=settings.collection_name,
                    vectors_config=VectorParams(
                        size=settings.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Created collection: {settings.collection_name}")
            else:
                print(f"📋 Collection already exists: {settings.collection_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
            return False
    
    def initialize_vector_store(self) -> QdrantVectorStore:
        """Initialize vector store with Qdrant client"""
        try:
            if not self.client:
                self.initialize_client()
            
            self.create_collection()
            
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=settings.collection_name,
                embedding=self.embedding_model
            )
            
            print(f"✅ Vector store initialized for collection: {settings.collection_name}")
            return self.vector_store
            
        except Exception as e:
            print(f"❌ Error initializing vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to vector store"""
        try:
            if not self.vector_store:
                self.initialize_vector_store()
            
            self.vector_store.add_documents(documents=documents)
            print(f"✅ Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            print(f"❌ Error adding documents: {e}")
            return False
    
    def get_retriever(self, top_k: Optional[int] = None):
        """Get retriever for similarity search"""
        if not self.vector_store:
            self.initialize_vector_store()
        
        search_kwargs = {"k": top_k or settings.retrieval_top_k}
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
    
    def search_similar_documents(self, query: str, top_k: Optional[int] = None) -> List[Document]:
        """Search for similar documents"""
        try:
            retriever = self.get_retriever(top_k)
            return retriever.invoke(query)
            
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            return []


