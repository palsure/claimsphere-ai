"""
Extraction Agent - Structured data extraction using ERNIE 5.0 Thinking via CAMEL-AI
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
    logger.warning("CAMEL-AI not available. Extraction Agent will use fallback mode.")


class ExtractionAgent(BaseAgent):
    """Agent for extracting structured claim data using ERNIE 5.0 Thinking"""
    
    def __init__(self):
        """Initialize Extraction Agent"""
        super().__init__(
            agent_name="Extraction",
            system_message="You are an expert at extracting structured information from insurance claim documents. Extract key information accurately and provide reasoning for your extractions."
        )
        
        self.agent = None
        self._initialize_agent()
        self.log_action("initialized")
    
    def _initialize_agent(self):
        """Initialize CAMEL-AI agent with ERNIE 5.0 Thinking"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Extraction Agent will use fallback.")
            return
        
        try:
            qianfan_api_key = os.getenv('QIANFAN_API_KEY')
            if not qianfan_api_key:
                logger.warning("QIANFAN_API_KEY not set. Extraction Agent will use fallback.")
                return
            
            # Create ERNIE 5.0 Thinking model
            model = ModelFactory.create(
                model_platform=ModelPlatformType.QIANFAN,
                model_type=ModelType.ERNIE_5_0_THINKING,
                model_config_dict=QianfanConfig(temperature=0.2).as_dict(),
            )
            
            # Create ChatAgent
            self.agent = ChatAgent(
                system_message=self.system_message,
                model=model
            )
            
            logger.info("Extraction Agent initialized with ERNIE 5.0 Thinking")
        except Exception as e:
            logger.error(f"Failed to initialize CAMEL-AI agent: {e}", exc_info=True)
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Extract structured claim information from OCR text
        
        Args:
            input_data: Can be:
                - OCR text (str)
                - Dict with 'ocr_text' and optional 'ocr_layout'
            **kwargs: Additional parameters
        
        Returns:
            Dictionary with extracted data:
            - data: Extracted claim fields
            - reasoning: Reasoning trace from ERNIE 5.0 Thinking
            - confidence: Overall confidence score
        """
        try:
            # Extract OCR text from input
            if isinstance(input_data, str):
                ocr_text = input_data
                layout_info = kwargs.get("layout_info")
            elif isinstance(input_data, dict):
                ocr_text = input_data.get("ocr_text", input_data.get("text", ""))
                layout_info = input_data.get("ocr_layout", input_data.get("layout"))
            else:
                return self.handle_error(
                    ValueError("Input must be string (OCR text) or dict with 'ocr_text'"),
                    {"input_type": type(input_data).__name__}
                )
            
            if not ocr_text or not ocr_text.strip():
                return {
                    "success": False,
                    "error": "No OCR text provided",
                    "data": {}
                }
            
            self.log_action("extraction_started", {"text_length": len(ocr_text)})
            
            # Truncate text if too long
            max_text_len = 4000
            truncated_text = ocr_text[:max_text_len] if len(ocr_text) > max_text_len else ocr_text
            
            # Build extraction prompt
            prompt = f"""You are an expert at extracting information from insurance claims, medical bills, and claim forms. 
Carefully analyze this document and extract key information.

DOCUMENT TEXT:
{truncated_text}

Extract and return a JSON object with these fields:
- claimant_name: The patient or member name (the person receiving service)
- provider_name: The hospital, clinic, or doctor name (who provided the service)
- date_of_incident: The service date (ISO format: YYYY-MM-DD)
- total_amount: The total claim/bill amount (number only, no currency symbol)
- currency: The currency code (USD, CNY, EUR, etc.)
- claim_type: One of: medical, dental, vision, pharmacy, hospital, mental_health, emergency, other
- policy_number: Insurance member ID or policy number if visible
- diagnosis: Any diagnosis or condition mentioned
- procedure: Any procedure or treatment mentioned
- description: Brief description of what the claim is for

Be precise. If a field is not clearly visible in the document, use null instead of guessing.
Return ONLY valid JSON, no other text or explanation."""
            
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
                    claim_data = self._parse_json_response(result_text)
                    
                    return {
                        "success": True,
                        "data": claim_data,
                        "reasoning": reasoning,
                        "confidence": 0.85,  # Default confidence
                        "method": "ERNIE_5_0_Thinking"
                    }
                except Exception as e:
                    logger.error(f"CAMEL-AI extraction failed: {e}", exc_info=True)
                    # Fallback to direct ERNIE API
                    return self._fallback_extraction(ocr_text)
            else:
                # Fallback to direct ERNIE API
                return self._fallback_extraction(ocr_text)
                
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
            text = text[json_start:json_end].strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except:
                    pass
            
            # Return empty dict if parsing fails
            logger.warning(f"Failed to parse JSON from response: {text[:200]}")
            return {}
    
    def _fallback_extraction(self, ocr_text: str) -> Dict[str, Any]:
        """Fallback to direct ERNIE API if CAMEL-AI is not available"""
        try:
            from backend.ernie_service import ErnieService
            ernie_service = ErnieService()
            claim_data = ernie_service.extract_claim_info(ocr_text)
            
            return {
                "success": True,
                "data": claim_data,
                "reasoning": "",
                "confidence": 0.75,
                "method": "ERNIE_API_Fallback"
            }
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
