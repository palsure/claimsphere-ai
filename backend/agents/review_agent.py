"""
Review Agent - Role-playing agent for reviewing claims using CAMEL-AI
This agent acts as a Senior Claims Reviewer who carefully examines claims
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

try:
    from camel.agents import ChatAgent
    from camel.configs import QianfanConfig
    from camel.models import ModelFactory
    from camel.types import ModelPlatformType, ModelType
    from camel.messages import BaseMessage
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    logger.warning("CAMEL-AI not available. Review Agent will use fallback mode.")


class ReviewAgent(BaseAgent):
    """
    Review Agent - Acts as a Senior Claims Reviewer
    
    Role: Carefully reviews claims, identifies issues, and provides recommendations
    """
    
    def __init__(self):
        """Initialize Review Agent with role-playing persona"""
        super().__init__(
            agent_name="Review",
            system_message="""You are a Senior Claims Reviewer with 15 years of experience in insurance claims processing. 
Your role is to carefully review insurance claims and provide detailed analysis.

Your responsibilities:
1. Review claim documents and extracted data thoroughly
2. Identify any inconsistencies, missing information, or red flags
3. Check compliance with insurance policies and regulations
4. Assess the validity and accuracy of claim information
5. Provide clear, professional recommendations

Your review style:
- Be thorough and detail-oriented
- Ask critical questions when information is unclear
- Consider both the claimant's perspective and company policies
- Provide balanced, fair assessments
- Always cite specific evidence from the claim data

Format your review as JSON with:
- overall_assessment: "approve", "deny", "pend", or "needs_more_info"
- confidence_level: 0.0 to 1.0
- key_findings: list of important observations
- concerns: list of any concerns or red flags
- recommendations: list of specific recommendations
- reasoning: detailed explanation of your assessment"""
        )
        
        self.agent = None
        self._initialize_agent()
        self.log_action("initialized")
    
    def _initialize_agent(self):
        """Initialize CAMEL-AI agent"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Review Agent will use fallback.")
            return
        
        api_key = os.getenv("QIANFAN_API_KEY")
        if not api_key:
            logger.warning("QIANFAN_API_KEY not set. Review Agent will use fallback.")
            return
        
        try:
            # Use ERNIE 5.0 Thinking for reasoning capabilities
            model = ModelFactory.create(
                model_platform=ModelPlatformType.QIANFAN,
                model_type=ModelType.ERNIE_5_0_THINKING,
                model_config_dict=QianfanConfig(temperature=0.3).as_dict()
            )
            
            system_message = BaseMessage.make_system_message(
                role_name="Senior Claims Reviewer",
                content=self.system_message
            )
            
            self.agent = ChatAgent(system_message=system_message, model=model)
            logger.info("Review Agent initialized with ERNIE 5.0 Thinking via CAMEL-AI")
        except Exception as e:
            logger.error(f"Failed to initialize Review Agent with CAMEL-AI: {e}", exc_info=True)
            self.agent = None
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Review a claim
        
        Args:
            input_data: Claim data dictionary with extracted information
            **kwargs: Additional parameters
        
        Returns:
            Review result with assessment and recommendations
        """
        self.log_action("review_started")
        
        try:
            if isinstance(input_data, str):
                # If input is just OCR text, extract first
                claim_data = {"ocr_text": input_data}
            else:
                claim_data = input_data
            
            # Prepare review prompt
            claim_json = json.dumps(claim_data, indent=2, default=str)
            
            prompt = f"""Review the following insurance claim and provide your assessment:

CLAIM DATA:
{claim_json}

Please provide a thorough review considering:
1. Completeness of information
2. Consistency across fields
3. Compliance with typical insurance policies
4. Any suspicious patterns or red flags
5. Overall validity of the claim

Return your assessment as a JSON object with the structure specified in your system message."""
            
            # Use CAMEL-AI agent if available
            if self.agent:
                try:
                    user_message = BaseMessage.make_user_message(
                        role_name="User",
                        content=prompt
                    )
                    response = self.agent.step(user_message)
                    
                    # Extract reasoning and content
                    reasoning = ""
                    if hasattr(response.msgs[0], 'reasoning_content') and response.msgs[0].reasoning_content:
                        reasoning = response.msgs[0].reasoning_content
                    
                    result_text = response.msgs[0].content
                    
                    # Parse JSON from response
                    review_result = self._parse_json_response(result_text)
                    
                    self.log_action("review_completed")
                    return {
                        "success": True,
                        "review": review_result,
                        "reasoning": reasoning,
                        "method": "ERNIE_5_0_Thinking_CAMEL"
                    }
                except Exception as e:
                    logger.error(f"CAMEL-AI review failed: {e}", exc_info=True)
                    return self._fallback_review(claim_data)
            else:
                return self._fallback_review(claim_data)
                
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from model response"""
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            if json_end > json_start:
                text = text[json_start:json_end].strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # If JSON parsing fails, create a structured response from text
            logger.warning("Failed to parse JSON, creating structured response from text")
            return {
                "overall_assessment": "needs_more_info",
                "confidence_level": 0.5,
                "key_findings": ["Could not parse structured review"],
                "concerns": [],
                "recommendations": ["Manual review required"],
                "reasoning": text[:500]  # First 500 chars
            }
    
    def _fallback_review(self, claim_data: Dict) -> Dict[str, Any]:
        """Fallback review using basic rules"""
        logger.info("Using fallback review method")
        
        concerns = []
        findings = []
        
        # Basic checks
        if not claim_data.get("claimant_name"):
            concerns.append("Missing claimant name")
        if not claim_data.get("total_amount") or claim_data.get("total_amount", 0) <= 0:
            concerns.append("Invalid or missing amount")
        if not claim_data.get("date_of_incident"):
            concerns.append("Missing date of incident")
        
        # Assessment
        if len(concerns) == 0:
            assessment = "approve"
            confidence = 0.7
        elif len(concerns) <= 2:
            assessment = "pend"
            confidence = 0.5
        else:
            assessment = "needs_more_info"
            confidence = 0.3
        
        return {
            "success": True,
            "review": {
                "overall_assessment": assessment,
                "confidence_level": confidence,
                "key_findings": findings or ["Basic review completed"],
                "concerns": concerns,
                "recommendations": ["Use CAMEL-AI for detailed review"],
                "reasoning": "Fallback review using basic rules"
            },
            "method": "fallback"
        }
