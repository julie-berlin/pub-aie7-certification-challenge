from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from ..models.chat_models import ChatRequest, ChatResponse, HealthResponse
from ..services.agentic_workflow_service import AgenticWorkflowService
from ..core.settings import settings

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
        response = workflow_service.process_ethics_consultation(request)
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing ethics consultation: {str(e)}"
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
        
        # Transform to match frontend expectations
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