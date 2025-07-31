from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..core.settings import settings


class EthicsAssessmentService:
    """Service for comprehensive ethics scenario assessment"""
    
    def __init__(self):
        self.model = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            openai_api_key=settings.openai_api_key
        )
        self._setup_prompt_chain()
    
    def _setup_prompt_chain(self):
        """Initialize assessment prompt template"""
        assessment_template = """
        You are a federal ethics compliance expert. Analyze the scenario using all available sources.

        SEARCH PLAN: {search_plan}
        USER CONTEXT: {user_context}
        QUESTION: {question}

        FEDERAL ETHICS CONTEXT:
        {federal_context}

        GENERAL ETHICS GUIDANCE:
        {general_results}

        PENALTY INFORMATION:
        {penalty_results}

        CURRENT GUIDANCE & PRECEDENTS:
        {guidance_results}

        Provide comprehensive assessment using all available sources:
        1. **Violation Type**: Specific ethics violation classification
        2. **Severity Assessment**: Minor, moderate, or serious with justification
        3. **Legal Penalties**: Criminal, civil, and administrative consequences
        4. **Immediate Actions**: Step-by-step corrective measures
        5. **Reporting Requirements**: Who to notify, deadlines, procedures
        6. **Prevention Strategy**: Long-term compliance measures

        Prioritize federal law, supplement with current web guidance.
        """
        
        self.chain = (
            ChatPromptTemplate.from_template(assessment_template) |
            self.model |
            StrOutputParser()
        )
    
    def assess_ethics_scenario(self, 
                             question: str,
                             search_plan: str,
                             user_context: Dict[str, Any],
                             federal_context: str,
                             general_results: str,
                             penalty_results: str,
                             guidance_results: str) -> str:
        """Generate comprehensive ethics assessment"""
        try:
            return self.chain.invoke({
                "question": question,
                "search_plan": search_plan,
                "user_context": str(user_context),
                "federal_context": federal_context,
                "general_results": general_results,
                "penalty_results": penalty_results,
                "guidance_results": guidance_results
            })
        except Exception as e:
            print(f"❌ Error in ethics assessment: {e}")
            return "Unable to generate assessment due to technical error."