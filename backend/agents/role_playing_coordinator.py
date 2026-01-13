"""
Role-Playing Coordinator - Manages role-playing conversations between Review and Approval agents
Uses CAMEL-AI's role-playing framework to simulate realistic claim review discussions
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from backend.agents.base_agent import BaseAgent
from backend.agents.review_agent import ReviewAgent
from backend.agents.approval_agent import ApprovalAgent

logger = logging.getLogger(__name__)

try:
    from camel.agents import ChatAgent
    from camel.configs import QianfanConfig, ChatGPTConfig
    from camel.models import ModelFactory
    from camel.models.ollama_model import OllamaModel
    from camel.types import ModelPlatformType, ModelType
    from camel.messages import BaseMessage
    CAMEL_AVAILABLE = True
except ImportError as e:
    CAMEL_AVAILABLE = False
    logger.warning(f"CAMEL-AI not available: {e}. Role-playing will use fallback mode.")


class RolePlayingCoordinator(BaseAgent):
    """
    Role-Playing Coordinator - Manages conversations between Review and Approval agents
    
    This coordinator facilitates role-playing where:
    1. Review Agent reviews the claim and provides assessment
    2. Approval Agent reviews the assessment and makes a decision
    3. They can discuss and debate (optional multi-turn conversation)
    """
    
    def __init__(self):
        """Initialize Role-Playing Coordinator"""
        super().__init__(
            agent_name="RolePlayingCoordinator",
            system_message="You coordinate role-playing conversations between claim reviewers and approvers."
        )
        
        self.review_agent = ReviewAgent()
        self.approval_agent = ApprovalAgent()
        self.log_action("initialized")
    
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Process a claim through role-playing review and approval
        
        Args:
            input_data: Claim data dictionary
            **kwargs: Additional parameters
                - enable_discussion: Whether to enable multi-turn discussion (default: False)
                - max_turns: Maximum discussion turns (default: 2)
        
        Returns:
            Complete result with review, discussion, and final decision
        """
        self.log_action("role_playing_started")
        
        try:
            claim_data = input_data if isinstance(input_data, dict) else {"claim_data": input_data}
            enable_discussion = kwargs.get("enable_discussion", False)
            max_turns = kwargs.get("max_turns", 2)
            
            result = {
                "workflow": "role_playing_review_approval",
                "steps": [],
                "final_decision": None
            }
            
            # Step 1: Review Agent reviews the claim
            self.log_action("step_review")
            review_result = self.review_agent.process(claim_data, **kwargs)
            result["steps"].append({
                "step": "review",
                "agent": "ReviewAgent",
                "result": review_result
            })
            
            if not review_result.get("success"):
                result["error"] = "Review failed"
                return result
            
            # Step 2: Optional discussion between agents
            discussion_log = []
            if enable_discussion and CAMEL_AVAILABLE:
                self.log_action("step_discussion")
                discussion_log = self._facilitate_discussion(
                    claim_data=claim_data,
                    review_result=review_result,
                    max_turns=max_turns
                )
                result["steps"].append({
                    "step": "discussion",
                    "turns": len(discussion_log),
                    "log": discussion_log
                })
            
            # Step 3: Approval Agent makes final decision
            self.log_action("step_approval")
            approval_result = self.approval_agent.process(
                claim_data,
                review_result=review_result,
                discussion_log=discussion_log,
                **kwargs
            )
            result["steps"].append({
                "step": "approval",
                "agent": "ApprovalAgent",
                "result": approval_result
            })
            
            result["final_decision"] = approval_result.get("decision", {})
            result["review"] = review_result.get("review", {})
            
            # Add warning if agents used fallback mode
            if review_result.get("method") == "fallback" or approval_result.get("method") == "fallback":
                result["warning"] = "phi3 OLLAMA model not available. Using fallback mode - manual processing is available."
            
            self.log_action("role_playing_completed")
            return result
            
        except Exception as e:
            return self.handle_error(e, {"input_type": type(input_data).__name__})
    
    def _facilitate_discussion(self, claim_data: Dict, review_result: Dict, max_turns: int = 2) -> List[Dict]:
        """
        Facilitate a discussion between Review and Approval agents
        
        This creates a multi-turn conversation where agents can ask questions,
        clarify concerns, and debate the claim before making a final decision.
        """
        discussion_log = []
        
        try:
            # Initialize discussion agents
            # Only use OLLAMA phi3/phi-3 mini
            # OpenAI and Qianfan disabled - not working
            use_ollama = os.getenv("USE_OLLAMA", "true").lower() in ("true", "1", "yes")
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
            openai_key = None  # Disabled - not working due to quota
            qianfan_key = None  # Disabled - not working
            
            # Check OLLAMA phi3 only
            if use_ollama and ollama_url:
                try:
                    import requests
                    logger.info(f"Checking OLLAMA availability at {ollama_url} for discussion...")
                    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
                    if response.status_code == 200:
                        models = response.json().get('models', [])
                        model_names = [m.get('name', '') for m in models]
                        
                        # Only use phi3 or phi-3 mini
                        ollama_model = None
                        if any('phi3' in name.lower() or 'phi-3' in name.lower() for name in model_names):
                            # Find the exact phi3 model name - prefer phi3:mini, then phi3
                            for name in model_names:
                                if 'phi3:mini' in name.lower() or 'phi-3:mini' in name.lower():
                                    ollama_model = 'phi3:mini'
                                    logger.info(f"Using {ollama_model} for discussion (phi3 mini - fastest)")
                                    break
                            if not ollama_model:
                                for name in model_names:
                                    if 'phi3' in name.lower() or 'phi-3' in name.lower():
                                        ollama_model = name.split(':')[0] if ':' in name else name
                                        logger.info(f"Using {ollama_model} for discussion (phi3 model)")
                                        break
                        else:
                            raise Exception("phi3/phi-3 mini model not found in OLLAMA")
                        
                        if ollama_model:
                            # Create OllamaModel with optimized settings for faster output
                            model = OllamaModel(
                                model_type=ollama_model,
                                model_config_dict={
                                    'temperature': 0.4,
                                    'max_tokens': 256  # Reduced from 512 for faster output
                                },
                                url=f'{ollama_url}/v1',  # OpenAI-compatible endpoint
                                timeout=90.0  # 90 seconds
                            )
                            model_name = f"OLLAMA ({ollama_model})"
                            logger.info(f"Discussion agents initialized with {model_name} via CAMEL-AI (90s timeout, 256 max tokens)")
                        else:
                            raise Exception("phi3:mini model not available")
                    else:
                        raise Exception(f"OLLAMA not responding: status {response.status_code}")
                except Exception as e:
                    logger.warning(f"OLLAMA phi3 not available: {e}. Discussion will be skipped - manual processing available.")
                    model = None
            elif not use_ollama:
                logger.info("USE_OLLAMA is disabled, skipping OLLAMA check")
                model = None
            else:
                model = None
            
            # OpenAI and Qianfan disabled - skip
            # If we reach here, phi3 failed or not available - discussion will be skipped
            if not model:
                logger.warning("phi3 OLLAMA model not available. Discussion will be skipped - manual processing available.")
                return discussion_log
            
            # Review Agent's perspective
            review_system = BaseMessage.make_system_message(
                role_name="Senior Claims Reviewer",
                content="""You are a Senior Claims Reviewer. You've reviewed the claim and provided your assessment.
You can answer questions from the Approver and provide additional details or clarifications about your review.
Be professional and helpful in your responses."""
            )
            
            # Approval Agent's perspective
            approval_system = BaseMessage.make_system_message(
                role_name="Claims Approver",
                content="""You are a Claims Approver. You've received the reviewer's assessment.
You can ask questions to clarify concerns, understand the reasoning better, or request additional information.
Be decisive but thorough in your questions."""
            )
            
            review_agent = ChatAgent(system_message=review_system, model=model, step_timeout=95.0)  # 90s + 5s buffer
            approval_agent = ChatAgent(system_message=approval_system, model=model, step_timeout=95.0)  # 90s + 5s buffer
            
            # Start discussion with compact JSON
            review_text = json.dumps(essential_review, default=str)  # Compact JSON (no indent)
            
            # Turn 1: Approver asks a question
            approver_prompt = f"""You've received this review assessment:

{review_text}

Based on this review, what questions or concerns do you have before making your decision?
Ask 1-2 specific questions that would help you make a better decision."""
            
            approver_message = BaseMessage.make_user_message(
                role_name="Claims Approver",
                content=approver_prompt
            )
            approver_response = approval_agent.step(approver_message)
            approver_question = approver_response.msgs[0].content
            
            discussion_log.append({
                "turn": 1,
                "speaker": "Approver",
                "message": approver_question
            })
            
            # Turn 2: Reviewer responds
            if max_turns >= 2:
                reviewer_prompt = f"""The Approver has asked: "{approver_question}"

Provide a helpful response based on your review of the claim. Be specific and reference the claim data."""
                
                reviewer_message = BaseMessage.make_user_message(
                    role_name="Senior Claims Reviewer",
                    content=reviewer_prompt
                )
                reviewer_response = review_agent.step(reviewer_message)
                reviewer_answer = reviewer_response.msgs[0].content
                
                discussion_log.append({
                    "turn": 2,
                    "speaker": "Reviewer",
                    "message": reviewer_answer
                })
            
            logger.info(f"Discussion completed with {len(discussion_log)} turns")
            
        except Exception as e:
            logger.error(f"Discussion facilitation failed: {e}", exc_info=True)
            # Continue without discussion
        
        return discussion_log
