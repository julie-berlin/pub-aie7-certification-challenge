from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..core.settings import settings


class ReflectionAgentService:
    """Service for quality assurance and confidence scoring"""
    
    def __init__(self):
        self.model = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            openai_api_key=settings.openai_api_key
        )
        self._setup_prompt_chain()
    
    def _setup_prompt_chain(self):
        """Initialize reflection prompt template"""
        reflection_template = """
        You are a quality assurance agent for federal ethics guidance. Review the response for accuracy, completeness, and usefulness.

        ORIGINAL QUESTION: {question}
        GENERATED RESPONSE: {response}

        Evaluate the response on:
        1. **Accuracy**: Are the legal citations and penalties correct?
        2. **Completeness**: Are all important aspects addressed?
        3. **Actionability**: Are next steps clear and specific?
        4. **Clarity**: Is the guidance understandable?
        5. **Risk Assessment**: Is the severity appropriately characterized?

        Provide:
        - Confidence score (0-100)
        - Areas that need improvement
        - Missing critical information
        - Overall quality assessment
        """
        
        self.chain = (
            ChatPromptTemplate.from_template(reflection_template) |
            self.model |
            StrOutputParser()
        )
    
    def reflect_on_response(self, question: str, response: str) -> Dict[str, Any]:
        """Generate quality reflection and extract confidence score"""
        try:
            reflection_text = self.chain.invoke({
                "question": question,
                "response": response
            })
            
            confidence_score = self._extract_confidence_score(reflection_text)
            
            return {
                "reflection": reflection_text,
                "confidence_score": confidence_score
            }
            
        except Exception as e:
            print(f"❌ Error in reflection: {e}")
            return {
                "reflection": "Unable to generate reflection due to technical error.",
                "confidence_score": 50.0
            }
    
    def _extract_confidence_score(self, reflection_text: str) -> float:
        """Extract confidence score from reflection text"""
        reflection_lower = reflection_text.lower()
        
        if "high confidence" in reflection_lower or "90" in reflection_text:
            return 90.0
        elif "low confidence" in reflection_lower or "60" in reflection_text:
            return 60.0
        elif "moderate confidence" in reflection_lower or "75" in reflection_text:
            return 75.0
        elif any(score in reflection_text for score in ["85", "80", "95"]):
            # Try to extract numeric score
            import re
            scores = re.findall(r'\b([6-9][0-9]|100)\b', reflection_text)
            if scores:
                return float(scores[0])
        
        return 85.0  # Default confidence