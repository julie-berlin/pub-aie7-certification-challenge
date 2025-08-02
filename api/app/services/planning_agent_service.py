from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..core.settings import settings


class PlanningAgentService:
    """Service for research planning using lightweight model"""
    
    def __init__(self):
        self.model = ChatOpenAI(
            model=settings.planning_model,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key
        )
        self._setup_prompt_chain()
    
    def _setup_prompt_chain(self):
        """Initialize planning prompt template"""
        planning_template = """
        You are a federal ethics research planning agent. Analyze the user's question to develop a comprehensive search and analysis strategy.

        USER QUESTION: {question}
        USER CONTEXT: {user_context}

        Create a structured research plan that includes:
        1. **Key Ethics Areas**: What specific federal ethics laws/regulations to focus on
        2. **Search Terms**: Targeted web search terms for current guidance
        3. **Risk Factors**: Potential aggravating or mitigating circumstances
        4. **Analysis Focus**: What aspects need the deepest investigation

        Provide a concise but thorough research plan.
        """
        
        self.chain = (
            ChatPromptTemplate.from_template(planning_template) | 
            self.model | 
            StrOutputParser()
        )
    
    def create_search_plan(self, question: str, user_context: Dict[str, Any]) -> str:
        """Generate research plan for ethics scenario"""
        try:
            return self.chain.invoke({
                "question": question,
                "user_context": str(user_context)
            })
        except Exception as e:
            print(f"❌ Error creating search plan: {e}")
            return "Standard ethics research approach"