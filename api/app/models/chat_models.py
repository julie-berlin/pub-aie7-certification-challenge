from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class UserRole(str, Enum):
    """Federal employee role types"""
    FEDERAL_EMPLOYEE = "federal_employee"
    CONTRACTOR = "contractor"
    SENIOR_EXECUTIVE = "senior_executive"
    PROCUREMENT_OFFICER = "procurement_officer"
    ETHICS_OFFICIAL = "ethics_official"


class SecurityClearance(str, Enum):
    """Security clearance levels"""
    NONE = "none"
    PUBLIC_TRUST = "public_trust"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


class UserContext(BaseModel):
    """User context information for personalized guidance"""
    role: UserRole = UserRole.FEDERAL_EMPLOYEE
    agency: Optional[str] = Field(None, description="Government agency or department")
    seniority: Optional[str] = Field("mid_level", description="Career level")
    clearance: SecurityClearance = SecurityClearance.NONE
    grade_level: Optional[str] = Field(None, description="GS level or equivalent")


class ChatRequest(BaseModel):
    """Request model for ethics chat consultation"""
    question: str = Field(..., description="Ethics question or scenario")
    user_context: Optional[UserContext] = Field(None, description="User context for personalized guidance")


class SearchResult(BaseModel):
    """Web search result structure"""
    title: str
    url: str
    content: str
    score: Optional[float] = None


class EthicsAssessment(BaseModel):
    """Structured ethics assessment response"""
    violation_type: Optional[str] = Field(None, description="Type of potential violation")
    severity_level: Optional[str] = Field(None, description="Minor, moderate, or serious")
    legal_penalties: Optional[str] = Field(None, description="Applicable penalties")
    immediate_actions: Optional[str] = Field(None, description="Required immediate steps")
    reporting_requirements: Optional[str] = Field(None, description="Who to notify and when")
    prevention_guidance: Optional[str] = Field(None, description="How to avoid similar issues")


class ChatResponse(BaseModel):
    """Response model for ethics chat consultation"""
    question: str
    response: str = Field(..., description="Comprehensive ethics guidance")
    
    # Optional structured assessment
    assessment: Optional[EthicsAssessment] = None
    
    
    # Source information
    federal_law_sources: int = Field(0, description="Number of federal law chunks used")
    web_sources: int = Field(0, description="Number of web sources consulted")
    search_results: List[SearchResult] = Field(default_factory=list)
    
    # Processing metadata
    processing_time_seconds: Optional[float] = None
    search_plan: Optional[str] = Field(None, description="Research strategy used")


class DocumentUploadRequest(BaseModel):
    """Request model for document upload metadata"""
    filename: str
    description: Optional[str] = None
    category: Optional[str] = Field("ethics_guidance", description="Document category")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    filename: str
    file_size: int
    chunks_created: int
    processing_time_seconds: float
    status: str = "processed"


class DocumentInfo(BaseModel):
    """Document information model"""
    document_id: str
    filename: str
    file_size: int
    upload_timestamp: str
    chunks_count: int
    category: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    environment: str
    services: Dict[str, str] = Field(default_factory=dict)