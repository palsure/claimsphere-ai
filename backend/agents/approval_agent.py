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
    from camel.configs import QianfanConfig, ChatGPTConfig
    from camel.models import ModelFactory
    from camel.models.ollama_model import OllamaModel
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
        """Initialize CAMEL-AI agent with OLLAMA (preferred), OpenAI, or Qianfan fallback"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Approval Agent will use fallback.")
            return
        
        # Only use phi3:mini OLLAMA model
        # OpenAI and Qianfan disabled - not working
        use_ollama = os.getenv("USE_OLLAMA", "true").lower() in ("true", "1", "yes")
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        openai_key = None  # Disabled - not working due to quota
        qianfan_key = None  # Disabled - not working
        
        model = None
        model_name = "fallback"
    
        try:
            # Only try OLLAMA phi3:mini (exact model name)
            if use_ollama and ollama_url:
                try:
                    import requests
                    logger.info(f"Checking OLLAMA availability at {ollama_url}...")
                    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
                    if response.status_code == 200:
                        models = response.json().get('models', [])
                        model_names = [m.get('name', '') for m in models]
                        
                        # Only use phi3:mini (exact match)
                        ollama_model = None
                        if any('phi3:mini' in name.lower() or 'phi-3:mini' in name.lower() for name in model_names):
                            ollama_model = 'phi3:mini'
                            logger.info(f"Using {ollama_model} (phi3:mini - optimized for speed)")
                        else:
                            logger.warning("phi3:mini model not found in OLLAMA. Manual processing will be used.")
                            model = None
                        
                        if ollama_model:
                            # Create OllamaModel with optimized settings for faster output
                            model = OllamaModel(
                                model_type=ollama_model,
                                model_config_dict={
                                    'temperature': 0.2,  # Lower temperature for more consistent decisions
                                    'max_tokens': 256  # Reduced from 512 for faster output
                                },
                                url=f'{ollama_url}/v1',  # OpenAI-compatible endpoint
                                timeout=90.0  # 90 second timeout
                            )
                            system_message = BaseMessage.make_system_message(
                                role_name="Claims Approver",
                                content=self.system_message
                            )
                            self.agent = ChatAgent(
                                system_message=system_message, 
                                model=model,
                                step_timeout=95.0  # Slightly longer than model timeout (90s + 5s buffer)
                            )
                            logger.info(f"Approval Agent initialized with OLLAMA ({ollama_model}) via CAMEL-AI (90s timeout, 256 max tokens)")
                            return
                    else:
                        logger.warning(f"OLLAMA returned status {response.status_code}. Manual processing will be used.")
                except Exception as e:
                    logger.warning(f"OLLAMA not available at {ollama_url}: {e}. Manual processing will be used.")
                    model = None

            # Qianfan disabled - skip
            # If we reach here, phi3 failed or not available - use manual processing
            if model is None:
                logger.warning("phi3 OLLAMA model not available. Approval Agent will use fallback mode. Manual review is available.")
                self.agent = None
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
            
            # Truncate data to avoid token limits
            essential_claim_fields = {
                'claimant_name': claim_data.get('claimant_name'),
                'total_amount': claim_data.get('total_amount'),
                'currency': claim_data.get('currency'),
                'date_of_incident': claim_data.get('date_of_incident') or claim_data.get('service_date'),
                'claim_type': claim_data.get('claim_type') or claim_data.get('category'),
            }
            essential_claim_fields = {k: v for k, v in essential_claim_fields.items() if v is not None}
            
            # Extract only essential review fields
            if review_result and isinstance(review_result, dict):
                review_data = review_result.get('review', review_result) if isinstance(review_result.get('review'), dict) else review_result
                essential_review = {
                    'recommendation': review_data.get('recommendation'),
                    'reasoning': (review_data.get('reasoning', '') or '')[:500],  # Limit reasoning
                    'issues_identified': review_data.get('issues_identified', [])[:5] if isinstance(review_data.get('issues_identified'), list) else None,  # Limit to 5 issues
                }
            else:
                essential_review = {'recommendation': None}
            essential_review = {k: v for k, v in essential_review.items() if v is not None}
            
            if self.agent:
                try:
                    claim_json = json.dumps(essential_claim_fields, default=str)  # Compact JSON (no indent)
                    review_json = json.dumps(essential_review, default=str) if essential_review else "No review provided"  # Compact JSON
                    
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
                    error_msg = str(e)
                    error_type = type(e).__name__
                    # Don't print full traceback - just log the error type and message
                    logger.error(f"CAMEL-AI decision failed: {error_type}: {error_msg[:200]}", exc_info=False)
                    
                    # Check for specific error types - fail fast, no retries
                    if "RateLimitError" in error_type or "429" in error_msg or "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                        logger.warning("OpenAI quota exceeded. Disabling agent and using fallback decision immediately (no retries).")
                        # Disable agent to prevent future retries
                        self.agent = None
                        return self._fallback_decision(claim_data, review_result)
                    elif "token" in error_msg.lower() or "limit" in error_msg.lower() or "exceeded" in error_msg.lower() or "context_length" in error_msg.lower():
                        logger.warning("Token limit exceeded. Using fallback decision immediately (no retries).")
                        return self._fallback_decision(claim_data, review_result)
                    elif "401" in error_msg or "invalid_appId" in error_msg or "permission" in error_msg.lower() or "authentication" in error_msg.lower():
                        logger.warning("API authentication failed. Disabling agent and using fallback decision immediately (no retries).")
                        # Disable agent to prevent future retries
                        self.agent = None
                        return self._fallback_decision(claim_data, review_result)
                    elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                        logger.warning("Request timed out. Using fallback decision immediately (no retries).")
                        return self._fallback_decision(claim_data, review_result)
                    else:
                        # For any other error, fail fast
                        logger.warning(f"AI decision failed ({error_type}). Using fallback decision immediately (no retries).")
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
