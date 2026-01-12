"""
Query Agent - Natural language queries with reasoning traces using ERNIE 5.0 Thinking
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
    logger.warning("CAMEL-AI not available. Query Agent will use fallback mode.")


class QueryAgent(BaseAgent):
    """Agent for handling natural language queries using ERNIE 5.0 Thinking"""
    
    def __init__(self):
        """Initialize Query Agent with CAMEL-AI ChatAgent"""
        super().__init__(
            agent_name="Query",
            system_message="""You are an expert claim analytics assistant powered by CAMEL-AI and ERNIE 5.0 Thinking.

Your role is to answer questions about insurance and medical claims with precision, clarity, and proper citations.

Key Responsibilities:
1. Analyze claim data and answer questions accurately
2. Always cite specific claim numbers when referencing claims
3. Provide clear explanations with reasoning
4. Use only information from the provided claims data
5. For aggregate questions, list all claim numbers used in calculations
6. If information is missing, state that clearly

Response Format:
- Provide a clear, factual answer
- Include reasoning when helpful
- Always cite claim numbers: "Claim CLM-20240112-ABC12345"
- List fields used: total_amount, status, category, etc.
- End with: CITED_CLAIMS: [list] and FIELDS_USED: [list]

Be professional, accurate, and helpful."""
        )
        
        self.agent = None
        self._initialize_agent()
        self.log_action("initialized")
    
    def _initialize_agent(self):
        """Initialize CAMEL-AI ChatAgent with ERNIE 5.0 Thinking"""
        if not CAMEL_AVAILABLE:
            logger.warning("CAMEL-AI not available. Query Agent will use fallback.")
            return
        
        try:
            qianfan_api_key = os.getenv('QIANFAN_API_KEY')
            if not qianfan_api_key:
                logger.warning("QIANFAN_API_KEY not set. Query Agent will use fallback.")
                return
            
            # Create ERNIE 5.0 Thinking model using CAMEL-AI ModelFactory
            model = ModelFactory.create(
                model_platform=ModelPlatformType.QIANFAN,
                model_type=ModelType.ERNIE_5_0_THINKING,
                model_config_dict=QianfanConfig(temperature=0.2).as_dict(),
            )
            
            # Create ChatAgent with system message
            # Using BaseMessage for proper message formatting
            system_message = BaseMessage.make_system_message(
                role_name="Claim Analytics Assistant",
                content=self.system_message
            )
            
            self.agent = ChatAgent(
                system_message=system_message,
                model=model
            )
            
            logger.info("Query Agent initialized with CAMEL-AI ChatAgent using ERNIE 5.0 Thinking")
        except Exception as e:
            logger.error(f"Failed to initialize CAMEL-AI ChatAgent: {e}", exc_info=True)
            self.agent = None
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Answer natural language query about claims
        
        Args:
            input_data: Query string or dict with 'query' key
            **kwargs: Additional parameters:
                - claims_context: List of claim dictionaries for context
                - scope_description: Description of data scope (for RBAC)
        
        Returns:
            Dictionary with query response:
            - answer: Answer text
            - reasoning: Reasoning trace from ERNIE 5.0 Thinking
            - cited_claims: List of claim numbers cited
            - fields_used: List of fields used in the answer
        """
        try:
            # Extract query
            if isinstance(input_data, str):
                query = input_data
            elif isinstance(input_data, dict):
                query = input_data.get("query", "")
            else:
                return self.handle_error(
                    ValueError("Input must be a query string or dict with 'query' key"),
                    {"input_type": type(input_data).__name__}
                )
            
            if not query or not query.strip():
                return {
                    "success": False,
                    "error": "Query is required",
                    "answer": ""
                }
            
            claims_context = kwargs.get("claims_context", [])
            scope_description = kwargs.get("scope_description", "available claims")
            
            self.log_action("query_processing_started", {
                "query_length": len(query),
                "claims_count": len(claims_context)
            })
            
            # Use CAMEL-AI agent if available
            if self.agent:
                try:
                    result = self._ai_query(query, claims_context, scope_description)
                    return result
                except Exception as e:
                    logger.error(f"AI query failed: {e}", exc_info=True)
                    # Fallback to direct ERNIE API
                    return self._fallback_query(query, claims_context, scope_description)
            else:
                # Fallback to direct ERNIE API
                return self._fallback_query(query, claims_context, scope_description)
                
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
    
    def _ai_query(self, query: str, claims_context: List[Dict], scope_description: str) -> Dict[str, Any]:
        """Process query using CAMEL-AI ChatAgent"""
        # Prepare context - limit to most recent 20 claims to avoid token limits
        context_summary = json.dumps(claims_context[-20:], indent=2, default=str)
        
        # Build comprehensive prompt with context
        prompt = f"""Answer the following question about insurance/medical claims.

CONTEXT:
- Data Scope: {scope_description}
- Total Claims Available: {len(claims_context)}
- Recent Claims Data (JSON):
{context_summary}

USER QUESTION: {query}

INSTRUCTIONS:
1. Analyze the claims data carefully
2. Answer the question accurately using only the provided data
3. Cite specific claim numbers when referencing claims (format: "Claim CLM-20240112-ABC12345")
4. For calculations, show which claims were included
5. If the answer cannot be determined from the data, state that clearly
6. Provide reasoning for complex answers

At the end of your response, include:
CITED_CLAIMS: [comma-separated list of claim_numbers used]
FIELDS_USED: [comma-separated list of fields used like total_amount, status, category, etc.]"""
        
        try:
            # Create user message using CAMEL-AI BaseMessage
            user_message = BaseMessage.make_user_message(
                role_name="User",
                content=prompt
            )
            
            # Step through the conversation using ChatAgent
            response = self.agent.step(user_message)
            
            # Extract reasoning and content
            reasoning = ""
            if hasattr(response.msgs[0], 'reasoning_content') and response.msgs[0].reasoning_content:
                reasoning = response.msgs[0].reasoning_content
            
            answer_text = response.msgs[0].content
            
            # Parse cited claims and fields
            cited_claims = []
            fields_used = []
            
            if "CITED_CLAIMS:" in answer_text:
                try:
                    cited_part = answer_text.split("CITED_CLAIMS:")[1].split("\n")[0]
                    cited_claims = [c.strip().strip("[]") for c in cited_part.split(",") if c.strip()]
                except:
                    pass
            
            if "FIELDS_USED:" in answer_text:
                try:
                    fields_part = answer_text.split("FIELDS_USED:")[1].split("\n")[0]
                    fields_used = [f.strip().strip("[]") for f in fields_part.split(",") if f.strip()]
                except:
                    pass
            
            # Clean up answer text
            clean_answer = answer_text
            if "CITED_CLAIMS:" in clean_answer:
                clean_answer = clean_answer.split("CITED_CLAIMS:")[0].strip()
            
            return {
                "success": True,
                "answer": clean_answer,
                "reasoning": reasoning,
                "cited_claims": cited_claims,
                "fields_used": fields_used,
                "claims_analyzed": len(claims_context),
                "method": "CAMEL-AI_ChatAgent_ERNIE_5_0_Thinking"
            }
        except Exception as e:
            logger.error(f"Error in ChatAgent step: {e}", exc_info=True)
            raise
    
    def _fallback_query(self, query: str, claims_context: List[Dict], scope_description: str) -> Dict[str, Any]:
        """Fallback to direct ERNIE API"""
        try:
            from backend.ernie_service import ErnieService
            ernie_service = ErnieService()
            answer = ernie_service.answer_claim_query(query, claims_context)
            
            return {
                "success": True,
                "answer": answer,
                "reasoning": "",
                "cited_claims": [],
                "fields_used": [],
                "claims_analyzed": len(claims_context),
                "method": "ERNIE_API_Fallback"
            }
        except Exception as e:
            logger.error(f"Fallback query failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "answer": "I couldn't process that query. Please try again."
            }
