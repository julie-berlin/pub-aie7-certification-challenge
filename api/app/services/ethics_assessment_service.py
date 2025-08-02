from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

from ..core.settings import settings
from ..models.chat_models import EthicsAssessment, SimplifiedAssessment, DetailedAspect, SeverityLevel


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
        self._setup_structured_chain()
    
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
    
    def _setup_structured_chain(self):
        """Initialize structured assessment prompt template"""
        structured_template = """
        You are a federal ethics compliance expert. Analyze the scenario and provide a structured assessment.

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

        You MUST respond with ONLY a valid JSON object in this exact format (no other text):

        {{
            "simplified": {{
                "direct_answer": "Clear statement of law/statute violated or 'No violation identified'",
                "severity": "minor",
                "immediate_action_required": true,
                "next_steps_summary": "Brief 1-2 sentence actionable next steps"
            }},
            "detailed_aspects": [
                {{
                    "title": "Legal Foundation",
                    "icon": "⚖️",
                    "content": "Detailed legal analysis with specific statutes and regulations"
                }},
                {{
                    "title": "Severity Assessment", 
                    "icon": "📊",
                    "content": "Detailed severity justification with factors considered"
                }},
                {{
                    "title": "Potential Penalties",
                    "icon": "⚠️", 
                    "content": "Criminal, civil, and administrative consequences with specifics"
                }},
                {{
                    "title": "Immediate Actions",
                    "icon": "🚨",
                    "content": "Step-by-step immediate corrective measures"
                }},
                {{
                    "title": "Reporting Requirements",
                    "icon": "📋",
                    "content": "Who to notify, deadlines, procedures, forms needed"
                }},
                {{
                    "title": "Prevention Strategy",
                    "icon": "🛡️",
                    "content": "Long-term compliance measures and best practices"
                }}
            ]
        }}

        IMPORTANT: 
        - severity must be exactly one of: "no_violation", "minor", "moderate", "serious"
        - immediate_action_required must be exactly true or false (boolean)
        - Return ONLY the JSON, no markdown formatting or extra text
        - Prioritize federal law, supplement with current web guidance
        """
        
        self.structured_chain = (
            ChatPromptTemplate.from_template(structured_template) |
            self.model |
            StrOutputParser()
        )

    def assess_ethics_scenario_structured(self, 
                                        question: str,
                                        search_plan: str,
                                        user_context: Dict[str, Any],
                                        federal_context: str,
                                        general_results: str,
                                        penalty_results: str,
                                        guidance_results: str) -> EthicsAssessment:
        """Generate structured ethics assessment with simplified and detailed views"""
        
        
        try:
            response = self.structured_chain.invoke({
                "question": question,
                "search_plan": search_plan,
                "user_context": str(user_context),
                "federal_context": federal_context,
                "general_results": general_results,
                "penalty_results": penalty_results,
                "guidance_results": guidance_results
            })
            
            # Parse JSON response
            try:
                # Clean the response of any markdown formatting
                clean_response = response.strip()
                if clean_response.startswith('```json'):
                    clean_response = clean_response[7:]
                if clean_response.endswith('```'):
                    clean_response = clean_response[:-3]
                clean_response = clean_response.strip()
                
                print(f"🔍 Attempting to parse JSON response: {clean_response[:200]}...")
                assessment_data = json.loads(clean_response)
                
                # Create structured assessment
                simplified = SimplifiedAssessment(
                    direct_answer=assessment_data["simplified"]["direct_answer"],
                    severity=SeverityLevel(assessment_data["simplified"]["severity"]),
                    immediate_action_required=assessment_data["simplified"]["immediate_action_required"],
                    next_steps_summary=assessment_data["simplified"]["next_steps_summary"]
                )
                
                detailed_aspects = [
                    DetailedAspect(
                        title=aspect["title"],
                        icon=aspect["icon"],
                        content=aspect["content"]
                    )
                    for aspect in assessment_data["detailed_aspects"]
                ]
                
                assessment = EthicsAssessment(
                    simplified=simplified,
                    detailed_aspects=detailed_aspects
                )
                print(f"✅ Successfully created structured assessment with {len(detailed_aspects)} aspects")
                return assessment
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ Error parsing structured response: {e}")
                print(f"❌ Raw response was: {repr(response)}")
                # Fallback to basic assessment
                return self._create_fallback_assessment(response)
                
        except Exception as e:
            print(f"❌ Error in structured ethics assessment: {e}")
            return self._create_fallback_assessment("Unable to generate assessment due to technical error.")
    
    def _create_fallback_assessment(self, response_text: str) -> EthicsAssessment:
        """Create fallback assessment when structured parsing fails"""
        # Try to extract key information from the text response
        direct_answer = "Assessment requires review of detailed analysis"
        severity = SeverityLevel.MODERATE
        immediate_action_required = True
        next_steps = "Consult with your ethics official for specific guidance"
        
        # Simple heuristics to improve the fallback
        if response_text:
            if "no violation" in response_text.lower() or "not inappropriate" in response_text.lower():
                severity = SeverityLevel.NO_VIOLATION
                immediate_action_required = False
                direct_answer = "No clear violation identified"
            elif "serious" in response_text.lower() or "significant" in response_text.lower():
                severity = SeverityLevel.SERIOUS
                direct_answer = "Potential serious ethics violation identified"
            elif "minor" in response_text.lower():
                severity = SeverityLevel.MINOR
                direct_answer = "Minor ethics concern identified"
            
            if "disclose" in response_text.lower() or "report" in response_text.lower():
                next_steps = "Disclose to your ethics official and follow agency procedures"
        
        return EthicsAssessment(
            simplified=SimplifiedAssessment(
                direct_answer=direct_answer,
                severity=severity,
                immediate_action_required=immediate_action_required,
                next_steps_summary=next_steps
            ),
            detailed_aspects=[
                DetailedAspect(
                    title="Complete Assessment",
                    icon="📄",
                    content=response_text if response_text else "No detailed assessment available"
                ),
                DetailedAspect(
                    title="Next Steps",
                    icon="🚨",
                    content="This assessment was generated using fallback processing. Please consult with your ethics official for authoritative guidance."
                )
            ]
        )