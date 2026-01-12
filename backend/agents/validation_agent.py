"""
Validation Agent - Rule-based and AI-powered validation using ERNIE 5.0 Thinking
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
    logger.warning("CAMEL-AI not available. Validation Agent will use fallback mode.")


class ValidationAgent(BaseAgent):
    """Agent for validating claims using ERNIE 5.0 Thinking"""
    
    def __init__(self):
        """Initialize Validation Agent"""
        super().__init__(
            agent_name="Validation",
            system_message="You are a claim validation expert. Analyze claims for compliance, accuracy, and completeness. Provide clear reasoning for your validation decisions."
        )
        
        self.agent = None
        self._initialize_agent()
        self.log_action("initialized")
    
    def _initialize_agent(self):
        """Initialize CAMEL-AI agent with ERNIE 5.0 Thinking"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Validation Agent will use fallback.")
            return
        
        try:
            qianfan_api_key = os.getenv('QIANFAN_API_KEY')
            if not qianfan_api_key:
                logger.warning("QIANFAN_API_KEY not set. Validation Agent will use fallback.")
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
            
            logger.info("Validation Agent initialized with ERNIE 5.0 Thinking")
        except Exception as e:
            logger.error(f"Failed to initialize CAMEL-AI agent: {e}", exc_info=True)
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Validate claim data
        
        Args:
            input_data: Claim data dictionary with extracted fields
            **kwargs: Additional parameters (validation_rules, plan_info, etc.)
        
        Returns:
            Dictionary with validation results:
            - is_valid: Boolean indicating if claim is valid
            - errors: List of validation errors
            - warnings: List of warnings
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
            
            self.log_action("validation_started", {"claim_id": claim_data.get("id")})
            
            # Basic rule-based validation
            rule_errors = self._basic_validation(claim_data)
            
            # AI-powered validation if agent is available
            ai_validation = {}
            if self.agent:
                try:
                    ai_validation = self._ai_validation(claim_data, **kwargs)
                except Exception as e:
                    logger.error(f"AI validation failed: {e}", exc_info=True)
            
            # Combine results
            all_errors = rule_errors.get("errors", []) + ai_validation.get("errors", [])
            all_warnings = rule_errors.get("warnings", []) + ai_validation.get("warnings", [])
            
            result = {
                "success": True,
                "is_valid": len(all_errors) == 0,
                "errors": all_errors,
                "warnings": all_warnings,
                "reasoning": ai_validation.get("reasoning", ""),
                "rule_validation": rule_errors,
                "ai_validation": ai_validation
            }
            
            self.log_action("validation_completed", {
                "is_valid": result["is_valid"],
                "error_count": len(all_errors)
            })
            
            return result
            
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
    
    def _basic_validation(self, claim_data: Dict) -> Dict[str, List[str]]:
        """Basic rule-based validation"""
        errors = []
        warnings = []
        
        # Required fields
        if not claim_data.get("claimant_name"):
            errors.append("Claimant name is required")
        
        if not claim_data.get("date_of_incident"):
            errors.append("Date of incident is required")
        elif claim_data.get("date_of_incident") and isinstance(claim_data["date_of_incident"], str):
            # Validate date format
            try:
                from datetime import datetime
                datetime.fromisoformat(claim_data["date_of_incident"])
            except:
                errors.append("Invalid date format for date_of_incident")
        
        if not claim_data.get("total_amount") or claim_data.get("total_amount", 0) <= 0:
            errors.append("Total amount must be greater than zero")
        
        # Warnings
        if not claim_data.get("policy_number"):
            warnings.append("Policy number is missing")
        
        if not claim_data.get("provider_name"):
            warnings.append("Provider name is missing")
        
        return {
            "errors": errors,
            "warnings": warnings
        }
    
    def _ai_validation(self, claim_data: Dict, **kwargs) -> Dict[str, Any]:
        """AI-powered validation using ERNIE 5.0 Thinking"""
        claim_json = json.dumps(claim_data, indent=2, default=str)
        validation_rules = kwargs.get("validation_rules", [])
        rules_text = json.dumps(validation_rules, indent=2) if validation_rules else "Standard insurance claim validation rules"
        
        prompt = f"""You are a claim validation expert. Review this claim data and provide validation feedback.

CLAIM DATA:
{claim_json}

VALIDATION RULES:
{rules_text}

Analyze the claim for:
1. Completeness - Are all required fields present?
2. Accuracy - Do the values make sense?
3. Consistency - Are dates, amounts, and other fields consistent?
4. Compliance - Does it meet insurance policy requirements?

Return a JSON object with:
- is_valid: boolean
- errors: array of error messages (critical issues)
- warnings: array of warning messages (non-critical issues)
- reasoning: your reasoning process

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
        validation_result = self._parse_json_response(result_text)
        
        return {
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
            "reasoning": reasoning,
            "ai_is_valid": validation_result.get("is_valid", True)
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
            
            logger.warning(f"Failed to parse JSON from validation response: {text[:200]}")
            return {"is_valid": True, "errors": [], "warnings": []}
