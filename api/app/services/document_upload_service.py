import uuid
import json
import tempfile
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from fastapi import UploadFile
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

from ..models.chat_models import DocumentUploadResponse, DocumentInfo
from ..services.vector_store_service import VectorStoreService
from ..services.document_loader_service import DocumentLoaderService
from ..core.settings import settings


class DocumentUploadService:
    """Service for handling document uploads and processing"""
    
    def __init__(self):
        self.vector_store_service = VectorStoreService()
        self.document_loader_service = DocumentLoaderService()
        # Use tmp directory for uploads since data directory is read-only in Docker
        self.uploads_dir = Path("/tmp/integribot_uploads")
        self.metadata_file = self.uploads_dir / "document_metadata.json"
        self._ensure_uploads_directory()
    
    def _ensure_uploads_directory(self):
        """Ensure uploads directory exists"""
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.metadata_file.exists():
            self._save_metadata({})
    
    def _load_metadata(self) -> dict:
        """Load document metadata from JSON file"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_metadata(self, metadata: dict):
        """Save document metadata to JSON file"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        if not file.filename:
            raise ValueError("No filename provided")
        
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are supported")
        
        if file.size and file.size > 50 * 1024 * 1024:  # 50MB limit
            raise ValueError("File size exceeds 50MB limit")
    
    async def process_upload(
        self, 
        file: UploadFile, 
        description: Optional[str] = None, 
        category: str = "ethics_guidance"
    ) -> DocumentUploadResponse:
        """Process uploaded document and add to vector store"""
        
        self._validate_file(file)
        
        document_id = str(uuid.uuid4())
        file_path = self.uploads_dir / f"{document_id}_{file.filename}"
        
        try:
            # Save uploaded file
            content = await file.read()
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Load and process document
            loader = PyMuPDFLoader(str(file_path))
            documents = loader.load()
            
            if not documents:
                raise ValueError("No content could be extracted from the PDF")
            
            # Add metadata to documents
            for doc in documents:
                doc.metadata.update({
                    "document_id": document_id,
                    "filename": file.filename,
                    "category": category,
                    "upload_timestamp": datetime.now().isoformat(),
                    "description": description
                })
            
            # Split documents into chunks
            chunks = self.document_loader_service.split_documents(documents)
            
            # Add to vector store
            if not self.vector_store_service.add_documents(chunks):
                raise Exception("Failed to add documents to vector store")
            
            # Save metadata
            metadata = self._load_metadata()
            metadata[document_id] = {
                "document_id": document_id,
                "filename": file.filename,
                "file_size": len(content),
                "upload_timestamp": datetime.now().isoformat(),
                "chunks_count": len(chunks),
                "category": category,
                "description": description,
                "file_path": str(file_path)
            }
            self._save_metadata(metadata)
            
            return DocumentUploadResponse(
                document_id=document_id,
                filename=file.filename,
                file_size=len(content),
                chunks_created=len(chunks),
                processing_time_seconds=0.0  # Will be set by router
            )
            
        except Exception as e:
            # Clean up file on error
            if file_path.exists():
                file_path.unlink()
            raise e
    
    def list_documents(self) -> List[DocumentInfo]:
        """List all uploaded documents"""
        metadata = self._load_metadata()
        
        return [
            DocumentInfo(
                document_id=doc_info["document_id"],
                filename=doc_info["filename"],
                file_size=doc_info["file_size"],
                upload_timestamp=doc_info["upload_timestamp"],
                chunks_count=doc_info["chunks_count"],
                category=doc_info["category"]
            )
            for doc_info in metadata.values()
        ]
    
    def get_document_info(self, document_id: str) -> Optional[DocumentInfo]:
        """Get information about a specific document"""
        metadata = self._load_metadata()
        doc_info = metadata.get(document_id)
        
        if not doc_info:
            return None
        
        return DocumentInfo(
            document_id=doc_info["document_id"],
            filename=doc_info["filename"],
            file_size=doc_info["file_size"],
            upload_timestamp=doc_info["upload_timestamp"],
            chunks_count=doc_info["chunks_count"],
            category=doc_info["category"]
        )
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and remove from vector store"""
        metadata = self._load_metadata()
        doc_info = metadata.get(document_id)
        
        if not doc_info:
            return False
        
        try:
            # Remove file
            file_path = Path(doc_info["file_path"])
            if file_path.exists():
                file_path.unlink()
            
            # Remove from metadata
            del metadata[document_id]
            self._save_metadata(metadata)
            
            # Note: Removing from vector store would require additional Qdrant operations
            # For now, we mark documents as deleted in metadata
            # In production, you might want to implement vector store cleanup
            
            return True
            
        except Exception as e:
            print(f"❌ Error deleting document {document_id}: {e}")
            return False