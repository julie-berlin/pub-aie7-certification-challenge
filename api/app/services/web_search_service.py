from typing import List, Dict, Any
from langchain_tavily import TavilySearch

from ..core.settings import settings
from ..core.logging_config import get_logger

logger = get_logger("app.services.web_search")


class WebSearchService:
    """Service for web search operations using Tavily"""
    
    def __init__(self):
        self.search_tool = TavilySearch(
            api_key=settings.tavily_api_key,
            max_results=3,
            search_depth="advanced",
            include_domains=["osg.gov", "oge.gov", "ethics.gov", "gsa.gov"]
        )
    
    def search_general_guidance(self, question: str) -> List[Dict[str, Any]]:
        """Search for general ethics guidance"""
        query = f"federal ethics violation {question} OGE guidance"
        return self._perform_search(query, "general_guidance")
    
    def search_penalty_information(self, question: str) -> List[Dict[str, Any]]:
        """Search for penalty and consequence information"""
        query = f"federal ethics penalties {question} criminal civil administrative"
        return self._perform_search(query, "penalty_research")
    
    def search_current_guidance(self, question: str) -> List[Dict[str, Any]]:
        """Search for current guidance and precedent cases"""
        query = f"ethics {question} reporting requirements precedent cases"
        return self._perform_search(query, "current_precedents")
    
    def _perform_search(self, query: str, search_type: str) -> List[Dict[str, Any]]:
        """Perform web search with error handling"""
        try:
            results = self.search_tool.invoke(query)
            
            # Add search type metadata
            for result in results:
                result["search_type"] = search_type
                result["query"] = query
            
            logger.info("Web search completed", extra={"search_type": search_type, "results_count": len(results), "query": query})
            return results
            
        except Exception as e:
            logger.error("Web search failed", extra={
                "search_type": search_type, 
                "error": str(e),
                "error_type": type(e).__name__,
                "query": query
            })
            return []
    
    def search_all_parallel(self, question: str) -> Dict[str, List[Dict[str, Any]]]:
        """Perform all search types - designed for parallel execution"""
        return {
            "general_web_results": self.search_general_guidance(question),
            "penalty_web_results": self.search_penalty_information(question),
            "guidance_web_results": self.search_current_guidance(question)
        }
    
    def combine_search_results(self, search_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Combine all search results into single list"""
        all_results = []
        
        for search_type, results in search_results.items():
            all_results.extend(results)
        
        return all_results


