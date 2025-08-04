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
        You are a federal ethics compliance expert. Analyze the scenario using all available sources and provide a comprehensive assessment in clear markdown format.

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

        Provide a comprehensive ethics assessment with the following structure:

        # Ethics Assessment

        ## Direct Answer
        [Clear statement of whether ethics laws/regulations are violated and which specific ones]

        ## Severity Level
        **[Minor/Moderate/Serious/No Violation]** - [Brief justification for severity level]

        ## Legal Foundation
        [Specific federal statutes, regulations, and ethical standards that apply]

        ## Potential Penalties
        [Criminal, civil, and administrative consequences with specifics]

        ## Immediate Actions Required
        [Step-by-step corrective measures that should be taken immediately]

        ## Reporting Requirements
        [Who to notify, deadlines, procedures, forms needed]

        ## Prevention Strategy
        [Long-term compliance measures and best practices to avoid similar issues]

        ## Additional Context
        [Any relevant precedents, guidance, or considerations based on user's role and agency]

        Prioritize federal law accuracy, provide specific citations when possible, and tailor guidance to the user's context.
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