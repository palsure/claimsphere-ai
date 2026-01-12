"""
Fraud Detection Agent - Risk assessment using ERNIE 5.0 Thinking reasoning
"""
import os
import json
import logging
from typing import Dict, Any, Optional
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
    logger.warning("CAMEL-AI not available. Fraud Detection Agent will use fallback mode.")


class FraudDetectionAgent(BaseAgent):
    """Agent for fraud detection and risk assessment using ERNIE 5.0 Thinking"""
    
    def __init__(self):
        """Initialize Fraud Detection Agent"""
        super().__init__(
            agent_name="FraudDetection",
            system_message="You are a fraud detection specialist. Identify suspicious patterns, anomalies, and risk factors in insurance claims. Provide detailed reasoning for your risk assessments."
        )
        
        self.agent = None
        self._initialize_agent()
        self.log_action("initialized")
    
    def _initialize_agent(self):
        """Initialize CAMEL-AI agent with ERNIE 5.0 Thinking"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Fraud Detection Agent will use fallback.")
            return
        
        try:
            qianfan_api_key = os.getenv('QIANFAN_API_KEY')
            if not qianfan_api_key:
                logger.warning("QIANFAN_API_KEY not set. Fraud Detection Agent will use fallback.")
                return
            
            model = ModelFactory.create(
                model_platform=ModelPlatformType.QIANFAN,
                model_type=ModelType.ERNIE_5_0_THINKING,
                model_config_dict=QianfanConfig(temperature=0.2).as_dict(),
            )
            
            self.agent = ChatAgent(
                system_message=self.system_message,
                model=model
            )
            
            logger.info("Fraud Detection Agent initialized with ERNIE 5.0 Thinking")
        except Exception as e:
            logger.error(f"Failed to initialize CAMEL-AI agent: {e}", exc_info=True)
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Assess fraud risk for a claim
        
        Args:
            input_data: Claim data dictionary
            **kwargs: Additional parameters (historical_claims, user_history, etc.)
        
        Returns:
            Dictionary with fraud risk assessment:
            - risk_score: Float between 0.0 (low risk) and 1.0 (high risk)
            - risk_level: "low", "medium", or "high"
            - risk_factors: List of identified risk factors
            - reasoning: Reasoning trace from ERNIE 5.0 Thinking
        """
        try:
            # Extract claim data
            if isinstance(input_data, dict):
                claim_data = input_data.get("extracted_data", input_data)
            else:
                return self.handle_error(
                    ValueError("Input must be a dictionary with claim data"),
                    {"input_type": type(input_data).__name__}
                )
            
            self.log_action("fraud_assessment_started", {"claim_id": claim_data.get("id")})
            
            # Basic risk indicators
            basic_risk = self._calculate_basic_risk(claim_data, **kwargs)
            
            # AI-powered fraud detection if agent is available
            ai_risk = {}
            if self.agent:
                try:
                    ai_risk = self._ai_fraud_detection(claim_data, **kwargs)
                except Exception as e:
                    logger.error(f"AI fraud detection failed: {e}", exc_info=True)
            
            # Combine basic and AI risk assessments
            risk_score = max(basic_risk.get("risk_score", 0.0), ai_risk.get("risk_score", 0.0))
            risk_factors = basic_risk.get("risk_factors", []) + ai_risk.get("risk_factors", [])
            
            # Determine risk level
            if risk_score >= 0.7:
                risk_level = "high"
            elif risk_score >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            result = {
                "success": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": list(set(risk_factors)),  # Remove duplicates
                "reasoning": ai_risk.get("reasoning", ""),
                "basic_risk": basic_risk,
                "ai_risk": ai_risk
            }
            
            self.log_action("fraud_assessment_completed", {
                "risk_score": risk_score,
                "risk_level": risk_level
            })
            
            return result
            
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
    
    def _calculate_basic_risk(self, claim_data: Dict, **kwargs) -> Dict[str, Any]:
        """Calculate basic risk indicators"""
        risk_score = 0.0
        risk_factors = []
        
        # Check for unusually high amounts
        total_amount = claim_data.get("total_amount", 0)
        if total_amount > 50000:
            risk_score += 0.2
            risk_factors.append("Unusually high claim amount")
        
        # Check for missing critical information
        if not claim_data.get("policy_number"):
            risk_score += 0.1
            risk_factors.append("Missing policy number")
        
        if not claim_data.get("provider_name"):
            risk_score += 0.1
            risk_factors.append("Missing provider information")
        
        # Check for duplicate matches
        duplicate_matches = kwargs.get("duplicate_matches", [])
        if duplicate_matches:
            risk_score += 0.3
            risk_factors.append(f"Potential duplicate: {len(duplicate_matches)} matches found")
        
        # Normalize risk score to 0-1 range
        risk_score = min(risk_score, 1.0)
        
        return {
            "risk_score": risk_score,
            "risk_factors": risk_factors
        }
    
    def _ai_fraud_detection(self, claim_data: Dict, **kwargs) -> Dict[str, Any]:
        """AI-powered fraud detection using ERNIE 5.0 Thinking"""
        claim_json = json.dumps(claim_data, indent=2, default=str)
        historical_context = kwargs.get("historical_claims", [])
        context_text = json.dumps(historical_context[:5], indent=2, default=str) if historical_context else "No historical data available"
        
        prompt = f"""You are a fraud detection specialist. Analyze this claim for potential fraud indicators.

CURRENT CLAIM:
{claim_json}

HISTORICAL CONTEXT (recent claims):
{context_text}

Analyze for:
1. Unusual patterns or anomalies
2. Inconsistencies in dates, amounts, or information
3. Suspicious provider or claimant behavior
4. Red flags that indicate potential fraud

Return a JSON object with:
- risk_score: float between 0.0 (low risk) and 1.0 (high risk)
- risk_factors: array of specific risk factors identified
- reasoning: your detailed reasoning process

Return ONLY valid JSON, no other text."""
        
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
        
        # Parse JSON
        fraud_result = self._parse_json_response(result_text)
        
        return {
            "risk_score": float(fraud_result.get("risk_score", 0.0)),
            "risk_factors": fraud_result.get("risk_factors", []),
            "reasoning": reasoning
        }
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON from model response"""
        if "```json" in text:
            json_start = text.find("```json") + 7
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        elif "```" in text:
            json_start = text.find("```") + 3
            json_end = text.find("```", json_start)
            text = text[json_start:json_end].strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except:
                    pass
            
            logger.warning(f"Failed to parse JSON from fraud detection response: {text[:200]}")
            return {"risk_score": 0.0, "risk_factors": []}
