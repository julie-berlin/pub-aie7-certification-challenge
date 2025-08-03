"""
Service for application startup tasks including collection initialization
"""

from typing import Dict, Any
from ..core.settings import settings
from ..core.logging_config import get_logger
from .document_loader_service import DocumentLoaderService
from .vector_store_service import VectorStoreService

logger = get_logger("app.services.startup")


class StartupService:
    """Handle application startup tasks"""
    
    def __init__(self):
        self.document_service = DocumentLoaderService()
        self.vector_service = VectorStoreService()
    
    def initialize_collections(self) -> Dict[str, Any]:
        """Initialize vector collections based on chunking strategy settings"""
        results = {
            "character_collection": {"created": False, "indexed": False, "count": 0},
            "semantic_collection": {"created": False, "indexed": False, "count": 0}
        }
        
        try:
            logger.info("Starting collection initialization", extra={
                "generate_both": settings.generate_both_collections,
                "default_strategy": settings.default_chunking_strategy
            })
            
            # Load base documents once
            base_documents = self.document_service.load_ethics_documents()
            if not base_documents:
                logger.error("No base documents loaded")
                return results
            
            # Always create both collections if generate_both_collections is True
            if settings.generate_both_collections:
                # Character-based collection
                results["character_collection"] = self._setup_character_collection(base_documents)
                
                # Semantic collection
                results["semantic_collection"] = self._setup_semantic_collection(base_documents)
            else:
                # Create only the default strategy collection
                if settings.default_chunking_strategy == "semantic":
                    results["semantic_collection"] = self._setup_semantic_collection(base_documents)
                else:
                    results["character_collection"] = self._setup_character_collection(base_documents)
            
            logger.info("Collection initialization completed", extra=results)
            return results
            
        except Exception as e:
            logger.error("Error during collection initialization", extra={"error": str(e)})
            raise
    
    def _setup_character_collection(self, base_documents) -> Dict[str, Any]:
        """Setup character-based chunking collection"""
        result = {"created": False, "indexed": False, "count": 0}
        
        try:
            logger.info("Setting up character-based collection")
            
            # Create collection
            collection_created = self.vector_service.create_collection(settings.collection_name)
            result["created"] = collection_created
            
            if collection_created:
                # Split documents using character-based chunking
                character_chunks = self.document_service.split_documents(base_documents)
                
                # Index documents
                indexed = self.vector_service.index_documents(
                    character_chunks, 
                    collection_name=settings.collection_name
                )
                result["indexed"] = indexed
                result["count"] = len(character_chunks) if indexed else 0
                
                logger.info("Character collection setup completed", extra=result)
            
        except Exception as e:
            logger.error("Error setting up character collection", extra={"error": str(e)})
        
        return result
    
    def _setup_semantic_collection(self, base_documents) -> Dict[str, Any]:
        """Setup semantic chunking collection"""
        result = {"created": False, "indexed": False, "count": 0}
        
        try:
            logger.info("Setting up semantic collection")
            
            # Create collection
            collection_created = self.vector_service.create_collection(settings.semantic_collection_name)
            result["created"] = collection_created
            
            if collection_created:
                # Split documents using semantic chunking
                semantic_chunks = self.document_service.semantic_split_documents(base_documents)
                
                # Index documents
                indexed = self.vector_service.index_documents(
                    semantic_chunks, 
                    collection_name=settings.semantic_collection_name
                )
                result["indexed"] = indexed
                result["count"] = len(semantic_chunks) if indexed else 0
                
                logger.info("Semantic collection setup completed", extra=result)
            
        except Exception as e:
            logger.error("Error setting up semantic collection", extra={"error": str(e)})
        
        return result
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        stats = {}
        
        try:
            # Character collection stats
            char_info = self.vector_service.get_collection_info(settings.collection_name)
            stats["character_collection"] = {
                "name": settings.collection_name,
                "vectors_count": char_info.get("vectors_count", 0),
                "status": char_info.get("status", "unknown")
            }
            
            # Semantic collection stats
            sem_info = self.vector_service.get_collection_info(settings.semantic_collection_name)
            stats["semantic_collection"] = {
                "name": settings.semantic_collection_name,
                "vectors_count": sem_info.get("vectors_count", 0),
                "status": sem_info.get("status", "unknown")
            }
            
        except Exception as e:
            logger.error("Error getting collection stats", extra={"error": str(e)})
        
        return stats
    
    def get_active_collection_name(self) -> str:
        """Get the currently active collection name based on settings"""
        if settings.default_chunking_strategy == "semantic":
            return settings.semantic_collection_name
        else:
            return settings.collection_name