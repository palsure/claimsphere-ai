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
    from camel.configs import QianfanConfig, ChatGPTConfig
    from camel.models import ModelFactory
    from camel.models.ollama_model import OllamaModel
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
        """Initialize CAMEL-AI agent with OLLAMA (preferred), OpenAI, or Qianfan fallback"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Review Agent will use fallback.")
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
                                    'temperature': 0.3,
                                    'max_tokens': 256  # Reduced from 512 for faster output
                                },
                                url=f'{ollama_url}/v1',  # OpenAI-compatible endpoint
                                timeout=90.0  # 90 second timeout
                            )
                            system_message = BaseMessage.make_system_message(
                                role_name="Senior Claims Reviewer",
                                content=self.system_message
                            )
                            self.agent = ChatAgent(
                                system_message=system_message, 
                                model=model,
                                step_timeout=95.0  # Slightly longer than model timeout (90s + 5s buffer)
                            )
                            logger.info(f"Review Agent initialized with OLLAMA ({ollama_model}) via CAMEL-AI (90s timeout, 256 max tokens)")
                            return
                    else:
                        logger.warning(f"OLLAMA returned status {response.status_code}. Manual processing will be used.")
                except Exception as e:
                    logger.warning(f"OLLAMA not available at {ollama_url}: {e}. Manual processing will be used.")
                    model = None

            # Qianfan disabled - skip
            # If we reach here, phi3 failed or not available - use manual processing
            if model is None:
                logger.warning("phi3 OLLAMA model not available. Review Agent will use fallback mode. Manual review is available.")
                self.agent = None
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
            
            # Truncate claim data to minimize tokens for faster output (keep only essential fields)
            essential_fields = {
                'claimant_name': claim_data.get('claimant_name'),
                'provider_name': claim_data.get('provider_name'),
                'total_amount': claim_data.get('total_amount'),
                'currency': claim_data.get('currency'),
                'date_of_incident': claim_data.get('date_of_incident') or claim_data.get('service_date'),
                'claim_type': claim_data.get('claim_type') or claim_data.get('category'),
                'policy_number': claim_data.get('policy_number'),
                'diagnosis': (claim_data.get('diagnosis') or '')[:100] if claim_data.get('diagnosis') else None,  # Limit to 100 chars
                'procedure': (claim_data.get('procedure') or '')[:100] if claim_data.get('procedure') else None,  # Limit to 100 chars
                'description': (claim_data.get('description', '') or '')[:200] if claim_data.get('description') else None,  # Limit to 200 chars
            }
            # Remove None values
            essential_fields = {k: v for k, v in essential_fields.items() if v is not None}
            
            # Prepare review prompt with minimal data for faster processing
            claim_json = json.dumps(essential_fields, default=str)  # Compact JSON (no indent)
            
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
                    # Step with timeout - fail fast on errors
                    try:
                        response = self.agent.step(user_message)
                    except Exception as step_error:
                        error_msg = str(step_error)
                        error_type = type(step_error).__name__
                        # Check for quota errors during step execution - fail immediately, no retries
                        if "RateLimitError" in error_type or "429" in error_msg or "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                            logger.warning("OpenAI quota exceeded during review. Using fallback immediately (no retries).")
                            # Disable OpenAI agent to prevent future retries
                            self.agent = None
                            return self._fallback_review(claim_data)
                        # Re-raise to be caught by outer exception handler
                        raise
                    
                    # Extract reasoning and content
                    reasoning = ""
                    if hasattr(response.msgs[0], 'reasoning_content') and response.msgs[0].reasoning_content:
                        reasoning = response.msgs[0].reasoning_content
                    
                    result_text = response.msgs[0].content
                    
                    # Parse JSON from response
                    review_result = self._parse_json_response(result_text)
                    
                    self.log_action("review_completed")
                    # Determine method based on model type
                    if os.getenv("OLLAMA_BASE_URL"):
                        method = "OLLAMA_CAMEL"
                    elif os.getenv("OPENAI_API_KEY"):
                        method = "OpenAI_CAMEL"
                    else:
                        method = "ERNIE_5_0_Thinking_CAMEL"
                    return {
                        "success": True,
                        "review": review_result,
                        "reasoning": reasoning,
                        "method": method
                    }
                except Exception as e:
                    error_msg = str(e)
                    error_type = type(e).__name__
                    logger.error(f"CAMEL-AI review failed ({error_type}): {error_msg[:200]}", exc_info=False)  # Don't print full traceback
                    # Check for specific error types - fail fast, no retries
                    if "RateLimitError" in error_type or "429" in error_msg or "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
                        logger.warning("API quota exceeded. Disabling agent and using fallback review immediately (no retries).")
                        # Disable agent to prevent future retries
                        self.agent = None
                        return self._fallback_review(claim_data)
                    elif "token" in error_msg.lower() or "limit" in error_msg.lower() or "exceeded" in error_msg.lower() or "context_length" in error_msg.lower():
                        logger.warning("Token limit exceeded. Using fallback review immediately (no retries).")
                        return self._fallback_review(claim_data)
                    elif "401" in error_msg or "invalid_appId" in error_msg or "permission" in error_msg.lower() or "authentication" in error_msg.lower():
                        logger.warning("API authentication failed. Disabling agent and using fallback review immediately (no retries).")
                        self.agent = None
                        return self._fallback_review(claim_data)
                    elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                        logger.warning("Request timed out. Using fallback review immediately (no retries).")
                        return self._fallback_review(claim_data)
                    else:
                        # For any other error, fail fast
                        logger.warning(f"AI review failed: {error_msg[:200]}. Using fallback review immediately (no retries).")
                        return self._fallback_review(claim_data)
            else:
                return self._fallback_review(claim_data)
                
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from model response, handling nested JSON strings"""
        # Try to extract JSON from markdown code blocks
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            if json_end > json_start:
                text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            if json_end > json_start:
                text = text[json_start:json_end].strip()
        
        try:
            parsed = json.loads(text)
            # If reasoning is a JSON string, parse it
            if isinstance(parsed.get("reasoning"), str):
                try:
                    reasoning_json = json.loads(parsed["reasoning"])
                    parsed["reasoning"] = reasoning_json
                except (json.JSONDecodeError, TypeError):
                    # Keep as string if it's not valid JSON
                    pass
            
            # Ensure required fields exist
            if "overall_assessment" not in parsed:
                # Try to extract from reasoning if it's a dict
                if isinstance(parsed.get("reasoning"), dict):
                    parsed["overall_assessment"] = parsed["reasoning"].get("overall_assessment", "needs_more_info")
                    parsed["confidence_level"] = parsed["reasoning"].get("confidence_level", 0.5)
                    if "key_findings" in parsed["reasoning"] and "key_findings" not in parsed:
                        parsed["key_findings"] = parsed["reasoning"]["key_findings"]
            
            return parsed
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract JSON from the text
            logger.warning(f"Failed to parse JSON directly: {e}. Attempting to extract JSON from text.")
            # Try to find JSON object in the text
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    # If reasoning is a JSON string, parse it
                    if isinstance(parsed.get("reasoning"), str):
                        try:
                            reasoning_json = json.loads(parsed["reasoning"])
                            parsed["reasoning"] = reasoning_json
                        except (json.JSONDecodeError, TypeError):
                            pass
                    return parsed
                except json.JSONDecodeError:
                    pass
            
            # If all parsing fails, create a structured response from text
            logger.warning("Could not parse JSON from response. Using fallback structure.")
            return {
                "recommendation": "PEND",
                "reasoning": text[:500] if text else "Review completed but response format was unexpected.",
                "issues_identified": ["Could not parse structured review response"],
                "required_actions": ["Manual review required"],
                "confidence_score": 0.5
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
