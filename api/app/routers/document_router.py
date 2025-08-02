from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import List, Optional
import uuid
import time
from pathlib import Path

from ..models.chat_models import DocumentUploadResponse, DocumentInfo
from ..services.document_upload_service import DocumentUploadService
from ..core.settings import settings

router = APIRouter(prefix="/api/documents", tags=["documents"])


def get_upload_service() -> DocumentUploadService:
    """Dependency injection for document upload service"""
    return DocumentUploadService()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    category: Optional[str] = Form("ethics_guidance"),
    upload_service: DocumentUploadService = Depends(get_upload_service)
) -> DocumentUploadResponse:
    """
    Upload and process a new document for the ethics knowledge base
    
    - **file**: PDF document file to upload
    - **description**: Optional description of the document
    - **category**: Document category (default: ethics_guidance)
    """
    try:
        start_time = time.time()
        
        response = await upload_service.process_upload(
            file=file,
            description=description,
            category=category or "ethics_guidance"
        )
        
        processing_time = time.time() - start_time
        response.processing_time_seconds = processing_time
        
        return response
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document upload: {str(e)}"
        )


@router.get("/list", response_model=List[DocumentInfo])
async def list_documents(
    upload_service: DocumentUploadService = Depends(get_upload_service)
) -> List[DocumentInfo]:
    """
    List all uploaded documents with metadata
    """
    try:
        return upload_service.list_documents()
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    upload_service: DocumentUploadService = Depends(get_upload_service)
) -> dict:
    """
    Delete a document and remove it from the vector store
    
    - **document_id**: UUID of the document to delete
    """
    try:
        success = await upload_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {document_id} not found"
            )
        
        return {"message": f"Document {document_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document_info(
    document_id: str,
    upload_service: DocumentUploadService = Depends(get_upload_service)
) -> DocumentInfo:
    """
    Get detailed information about a specific document
    
    - **document_id**: UUID of the document
    """
    try:
        document_info = upload_service.get_document_info(document_id)
        
        if not document_info:
            raise HTTPException(
                status_code=404,
                detail=f"Document with ID {document_id} not found"
            )
        
        return document_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving document info: {str(e)}"
        )