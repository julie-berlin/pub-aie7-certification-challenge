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

        Provide a structured JSON response with the following format:
        {{
            "simplified": {{
                "direct_answer": "Clear statement of law/statute violated or 'No violation identified'",
                "severity": "minor|moderate|serious|no_violation",
                "immediate_action_required": true/false,
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

        Return only valid JSON. Prioritize federal law, supplement with current web guidance.
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
                assessment_data = json.loads(response)
                
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
                
                return EthicsAssessment(
                    simplified=simplified,
                    detailed_aspects=detailed_aspects
                )
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ Error parsing structured response: {e}")
                # Fallback to basic assessment
                return self._create_fallback_assessment(response)
                
        except Exception as e:
            print(f"❌ Error in structured ethics assessment: {e}")
            return self._create_fallback_assessment("Unable to generate assessment due to technical error.")
    
    def _create_fallback_assessment(self, response_text: str) -> EthicsAssessment:
        """Create fallback assessment when structured parsing fails"""
        return EthicsAssessment(
            simplified=SimplifiedAssessment(
                direct_answer="Assessment could not be structured properly",
                severity=SeverityLevel.MODERATE,
                immediate_action_required=True,
                next_steps_summary="Review the detailed response for guidance"
            ),
            detailed_aspects=[
                DetailedAspect(
                    title="Full Assessment",
                    icon="📄",
                    content=response_text
                )
            ]
        )