from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import json

from ..models.chat_models import ChatRequest, ChatResponse, HealthResponse
from ..services.agentic_workflow_service import AgenticWorkflowService
from ..core.settings import settings
from ..core.logging_config import get_logger

logger = get_logger("app.api.chat")

router = APIRouter(prefix="/api", tags=["chat"])

# Dependency to get workflow service
def get_workflow_service() -> AgenticWorkflowService:
    """Dependency injection for workflow service"""
    return AgenticWorkflowService()


@router.post("/chat", response_model=ChatResponse)
async def ethics_consultation(
    request: ChatRequest,
    workflow_service: AgenticWorkflowService = Depends(get_workflow_service)
) -> ChatResponse:
    """
    Process ethics consultation request through agentic workflow
    
    - **question**: Ethics question or scenario description
    - **user_context**: Optional user context (role, agency, clearance)
    """
    try:
        logger.info("Processing ethics consultation", extra={
            "question_length": len(request.question),
            "has_user_context": request.user_context is not None
        })
        
        response = workflow_service.process_ethics_consultation(request)
        
        logger.info("Ethics consultation completed", extra={
            "processing_time": response.processing_time_seconds,
            "federal_sources": response.federal_law_sources,
            "web_sources": response.web_sources
        })
        
        return response
        
    except Exception as e:
        logger.error("Error processing ethics consultation", extra={
            "error": str(e),
            "question_length": len(request.question)
        })
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing ethics consultation: {str(e)}"
        )


@router.post("/chat/stream")
async def ethics_consultation_stream(
    request: ChatRequest,
    workflow_service: AgenticWorkflowService = Depends(get_workflow_service)
):
    """
    Process ethics consultation with streaming response
    
    - **question**: Ethics question or scenario description
    - **user_context**: Optional user context (role, agency, clearance)
    """
    
    async def generate_stream():
        try:
            logger.info("Starting streaming ethics consultation", extra={
                "question_length": len(request.question),
                "has_user_context": request.user_context is not None
            })
            
            # Send initial status
            yield f"data: {json.dumps({'status': 'analyzing_question', 'message': 'Analyzing your ethics question...'})}\n\n"
            
            # Send progress updates as the workflow processes
            yield f"data: {json.dumps({'status': 'retrieving_knowledge', 'message': 'Searching federal ethics law database...'})}\n\n"
            
            # Process the consultation (this will be enhanced to support real streaming later)
            response = workflow_service.process_ethics_consultation(request)
            
            yield f"data: {json.dumps({'status': 'generating_response', 'message': 'Generating comprehensive assessment...'})}\n\n"
            
            # Send the final response
            final_data = {
                'status': 'complete',
                'response': response.response,
                'searchPlan': response.search_plan,
                'sources': {
                    'federalLawChunks': response.federal_law_sources,
                    'webSources': response.web_sources
                },
                'processingTime': response.processing_time_seconds
            }
            
            yield f"data: {json.dumps(final_data)}\n\n"
            yield "data: [DONE]\n\n"
            
            logger.info("Streaming ethics consultation completed", extra={
                "processing_time": response.processing_time_seconds,
                "federal_sources": response.federal_law_sources,
                "web_sources": response.web_sources
            })
            
        except Exception as e:
            logger.error("Error in streaming ethics consultation", extra={
                "error": str(e),
                "question_length": len(request.question)
            })
            
            error_data = {
                'status': 'error',
                'error': f"Error processing ethics consultation: {str(e)}"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    try:
        # Basic service checks could be added here
        services_status = {
            "qdrant": "healthy",  # Could ping Qdrant
            "openai": "healthy",  # Could check API key
            "tavily": "healthy"   # Could check API key
        }
        
        return HealthResponse(
            status="healthy",
            version=settings.api_version,
            environment=settings.environment,
            services=services_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.post("/assess")
async def assess_ethics_violation(
    request: ChatRequest,
    workflow_service: AgenticWorkflowService = Depends(get_workflow_service)
) -> dict:
    """
    Assess ethics violation - compatible with frontend expectations
    
    - **question**: Ethics question or scenario description  
    - **user_context**: User context (role, agency, clearance)
    """
    try:
        response = workflow_service.process_ethics_consultation(request)
        
        logger.debug("Assessment response details", extra={
            "response_length": len(response.response),
            "search_plan": response.search_plan
        })
        
        # Transform to match frontend expectations (simplified response format)
        return {
            "response": response.response,
            "searchPlan": response.search_plan,
            "sources": {
                "federalLawChunks": response.federal_law_sources,
                "webSources": response.web_sources
            }
        }
        
    except Exception as e:
        return {
            "response": "I apologize, but I encountered an error processing your request. Please try again.",
            "error": f"Error processing ethics assessment: {str(e)}"
        }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "Federal Ethics Chatbot API is running"}