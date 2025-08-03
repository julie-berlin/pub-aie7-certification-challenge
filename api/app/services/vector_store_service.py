from typing import List, Optional
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from ..core.settings import settings
from ..core.logging_config import get_logger

logger = get_logger("app.services.vector_store")


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
            
            logger.info("Connected to Qdrant", extra={"qdrant_url": settings.qdrant_url})
            return self.client
            
        except Exception as e:
            logger.error("Failed to connect to Qdrant", extra={"error": str(e), "qdrant_url": settings.qdrant_url})
            raise
    
    def create_collection(self) -> bool:
        """Create ethics knowledge collection if it doesn't exist"""
        try:
            if not self.client:
                self.initialize_client()
            
            # Check if collection already exists
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
                logger.info("Created collection", extra={"collection_name": settings.collection_name})
            else:
                logger.info("Collection already exists", extra={"collection_name": settings.collection_name})
            
            return True
            
        except Exception as e:
            # Check if the error is specifically about collection already existing
            error_str = str(e).lower()
            if "already exists" in error_str or "conflict" in error_str:
                logger.info("Collection already exists (from exception)", extra={"collection_name": settings.collection_name})
                return True
            else:
                logger.error("Error creating collection", extra={"error": str(e), "collection_name": settings.collection_name})
                return False
    
    def initialize_vector_store(self) -> QdrantVectorStore:
        """Initialize vector store with Qdrant client"""
        try:
            if not self.client:
                self.initialize_client()
            
            # Try to create collection, but don't fail if it already exists
            collection_created = self.create_collection()
            if not collection_created:
                # Collection creation failed, but it might already exist
                # Try to proceed with vector store initialization anyway
                logger.warning("Collection creation returned False, attempting to use existing collection")
            
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=settings.collection_name,
                embedding=self.embedding_model
            )
            
            logger.info("Vector store initialized", extra={"collection_name": settings.collection_name})
            return self.vector_store
            
        except Exception as e:
            logger.error("Error initializing vector store", extra={"error": str(e)})
            raise
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to vector store"""
        try:
            if not self.vector_store:
                self.initialize_vector_store()
            
            self.vector_store.add_documents(documents=documents)
            logger.info("Added documents to vector store", extra={"document_count": len(documents)})
            return True
            
        except Exception as e:
            logger.error("Error adding documents", extra={"error": str(e)})
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
            logger.error("Error searching documents", extra={"error": str(e), "query": query})
            return []


