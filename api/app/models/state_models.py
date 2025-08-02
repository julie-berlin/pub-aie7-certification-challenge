from typing_extensions import TypedDict
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from .chat_models import EthicsAssessment


class ParallelEthicsState(TypedDict):
    """State model for parallel agentic workflow"""
    
    # Input
    question: str
    user_context: Optional[Dict[str, Any]]
    
    # Planning
    search_plan: Optional[str]
    
    # Knowledge retrieval
    context: List[Document]
    
    # Parallel web search results
    general_web_results: List[Dict[str, Any]]
    penalty_web_results: List[Dict[str, Any]]
    guidance_web_results: List[Dict[str, Any]]
    
    # Combined results
    web_results: List[Dict[str, Any]]
    
    # Assessment
    assessment: Optional[EthicsAssessment]
    response: str
    
    
    # Metadata
    processing_start_time: Optional[float]
    processing_time_seconds: Optional[float]