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
    from camel.configs import QianfanConfig
    from camel.models import ModelFactory
    from camel.types import ModelPlatformType, ModelType
    from camel.messages import BaseMessage, ChatMessage
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    logger.warning("CAMEL-AI not available. Role-playing will use fallback mode.")


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
            api_key = os.getenv("QIANFAN_API_KEY")
            if not api_key:
                logger.warning("Cannot facilitate discussion without QIANFAN_API_KEY")
                return discussion_log
            
            model = ModelFactory.create(
                model_platform=ModelPlatformType.QIANFAN,
                model_type=ModelType.ERNIE_5_0_THINKING,
                model_config_dict=QianfanConfig(temperature=0.4).as_dict()
            )
            
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
            
            review_agent = ChatAgent(system_message=review_system, model=model)
            approval_agent = ChatAgent(system_message=approval_system, model=model)
            
            # Start discussion
            review_assessment = review_result.get("review", {})
            review_text = json.dumps(review_assessment, indent=2)
            
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
