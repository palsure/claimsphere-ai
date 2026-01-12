"""
Approval Agent - Role-playing agent for making approval decisions using CAMEL-AI
This agent acts as a Claims Approver who makes final decisions based on reviews
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
    logger.warning("CAMEL-AI not available. Approval Agent will use fallback mode.")


class ApprovalAgent(BaseAgent):
    """
    Approval Agent - Acts as a Claims Approver
    
    Role: Makes final approval decisions based on reviews and company policies
    """
    
    def __init__(self):
        """Initialize Approval Agent with role-playing persona"""
        super().__init__(
            agent_name="Approval",
            system_message="""You are a Claims Approver with authority to make final decisions on insurance claims.
Your role is to make approval decisions based on reviews and company policies.

Your responsibilities:
1. Review the reviewer's assessment and recommendations
2. Consider company policies, regulations, and risk tolerance
3. Make final decisions: APPROVE, DENY, or PEND (request more information)
4. Set approved amounts when approving claims
5. Provide clear reasoning for your decisions

Your decision-making style:
- Be decisive but fair
- Consider both business needs and customer service
- Follow company policies strictly
- Balance risk and customer satisfaction
- Always provide clear justification

Decision criteria:
- APPROVE: Claim is valid, complete, and within policy limits
- DENY: Claim violates policy, is fraudulent, or is clearly invalid
- PEND: Need more information before making a decision

Format your decision as JSON with:
- decision: "approve", "deny", or "pend"
- approved_amount: number (if approving, can be less than claimed amount)
- confidence: 0.0 to 1.0
- reasoning: detailed explanation of your decision
- policy_references: list of policies or rules that influenced the decision
- conditions: list of any conditions attached to approval (if applicable)"""
        )
        
        self.agent = None
        self._initialize_agent()
        self.log_action("initialized")
    
    def _initialize_agent(self):
        """Initialize CAMEL-AI agent"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Approval Agent will use fallback.")
            return
        
        api_key = os.getenv("QIANFAN_API_KEY")
        if not api_key:
            logger.warning("QIANFAN_API_KEY not set. Approval Agent will use fallback.")
            return
        
        try:
            # Use ERNIE 5.0 Thinking for reasoning capabilities
            model = ModelFactory.create(
                model_platform=ModelPlatformType.QIANFAN,
                model_type=ModelType.ERNIE_5_0_THINKING,
                model_config_dict=QianfanConfig(temperature=0.2).as_dict()  # Lower temperature for more consistent decisions
            )
            
            system_message = BaseMessage.make_system_message(
                role_name="Claims Approver",
                content=self.system_message
            )
            
            self.agent = ChatAgent(system_message=system_message, model=model)
            logger.info("Approval Agent initialized with ERNIE 5.0 Thinking via CAMEL-AI")
        except Exception as e:
            logger.error(f"Failed to initialize Approval Agent with CAMEL-AI: {e}", exc_info=True)
            self.agent = None
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Make an approval decision
        
        Args:
            input_data: Dictionary containing claim data and review results
            **kwargs: Additional parameters (review_result, policy_rules, etc.)
        
        Returns:
            Decision result with approval decision and reasoning
        """
        self.log_action("decision_started")
        
        try:
            # Extract review result and claim data
            review_result = kwargs.get("review_result") or input_data.get("review_result")
            claim_data = input_data.get("claim_data") or input_data
            
            # Prepare decision prompt
            claim_json = json.dumps(claim_data, indent=2, default=str)
            review_json = json.dumps(review_result, indent=2, default=str) if review_result else "No review provided"
            
            prompt = f"""Make a final decision on this insurance claim based on the reviewer's assessment:

CLAIM DATA:
{claim_json}

REVIEWER'S ASSESSMENT:
{review_json}

Consider:
1. The reviewer's findings and recommendations
2. Company policies and risk tolerance
3. The completeness and validity of the claim
4. Any fraud risk indicators

Make your decision and provide clear reasoning. Return as JSON with the structure specified in your system message."""
            
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
                    decision_result = self._parse_json_response(result_text)
                    
                    self.log_action("decision_completed")
                    return {
                        "success": True,
                        "decision": decision_result,
                        "reasoning": reasoning,
                        "method": "ERNIE_5_0_Thinking_CAMEL"
                    }
                except Exception as e:
                    logger.error(f"CAMEL-AI decision failed: {e}", exc_info=True)
                    return self._fallback_decision(claim_data, review_result)
            else:
                return self._fallback_decision(claim_data, review_result)
                
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
            logger.warning("Failed to parse JSON, creating structured response from text")
            return {
                "decision": "pend",
                "approved_amount": None,
                "confidence": 0.5,
                "reasoning": text[:500],
                "policy_references": [],
                "conditions": []
            }
    
    def _fallback_decision(self, claim_data: Dict, review_result: Optional[Dict]) -> Dict[str, Any]:
        """Fallback decision using basic rules"""
        logger.info("Using fallback decision method")
        
        # Use review result if available
        if review_result and review_result.get("review"):
            review = review_result["review"]
            assessment = review.get("overall_assessment", "pend")
            
            if assessment == "approve":
                decision = "approve"
                approved_amount = claim_data.get("total_amount", 0)
            elif assessment == "deny":
                decision = "deny"
                approved_amount = 0
            else:
                decision = "pend"
                approved_amount = None
        else:
            # Basic decision based on claim data
            if claim_data.get("total_amount", 0) > 0:
                decision = "approve"
                approved_amount = claim_data.get("total_amount", 0)
            else:
                decision = "pend"
                approved_amount = None
        
        return {
            "success": True,
            "decision": {
                "decision": decision,
                "approved_amount": approved_amount,
                "confidence": 0.6,
                "reasoning": "Fallback decision using basic rules",
                "policy_references": [],
                "conditions": []
            },
            "method": "fallback"
        }
