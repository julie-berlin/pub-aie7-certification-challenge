from typing import List, Dict, Any
from langchain_community.tools.tavily_search import TavilySearchResults

from ..core.settings import settings


class WebSearchService:
    """Service for web search operations using Tavily"""
    
    def __init__(self):
        self.search_tool = TavilySearchResults(
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
            
            print(f"🔍 {search_type}: Found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"⚠️ {search_type} search failed: {e}")
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


