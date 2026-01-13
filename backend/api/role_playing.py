"""
API endpoints for role-playing claim review and approval
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.database.config import get_db
from backend.database.models import Claim, ClaimStatus, DecisionType, RoleType
from backend.auth.dependencies import get_current_user, require_any_role
from backend.agents.role_playing_coordinator import RolePlayingCoordinator
from backend.services.agent_coordinator import get_agent_coordinator
from backend.api.claims import get_claimant_name
from datetime import datetime

router = APIRouter(prefix="/claims", tags=["role-playing"])


class RolePlayingReviewRequest(BaseModel):
    """Request for role-playing review"""
    enable_discussion: bool = False
    max_turns: int = 2


class RolePlayingReviewResponse(BaseModel):
    """Response from role-playing review"""
    claim_id: str
    review: Dict[str, Any]
    discussion: Optional[Dict[str, Any]] = None
    decision: Dict[str, Any]
    reasoning_traces: Dict[str, Any]


@router.post("/{claim_id}/role-playing-review", response_model=RolePlayingReviewResponse)
async def role_playing_review(
    claim_id: str,
    request: RolePlayingReviewRequest,
    current_user = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),  # Only agents and admins
    db: Session = Depends(get_db)
):
    """
    Review and approve a claim using role-playing agents
    
    This endpoint uses CAMEL-AI role-playing where:
    - Review Agent acts as a Senior Claims Reviewer
    - Approval Agent acts as a Claims Approver
    - They can discuss and debate before making a decision
    
    Args:
        claim_id: ID of the claim to review
        request: Review request with options
        current_user: Current authenticated user (must be agent or admin)
        db: Database session
    
    Returns:
        Review and decision result with reasoning traces
    """
    # Get claim
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Authorization is already checked by require_any_role decorator
    
    # Check claim status - allow review for submitted claims
    if claim.status not in [ClaimStatus.PENDING_REVIEW, ClaimStatus.SUBMITTED, ClaimStatus.VALIDATED, ClaimStatus.EXTRACTED]:
        raise HTTPException(
            status_code=400,
            detail=f"Claim is not ready for review. Current status: {claim.status.value}"
        )
    
    try:
        # Initialize role-playing coordinator
        coordinator = RolePlayingCoordinator()
        
        # Prepare claim data
        claim_data = {
            "claim_id": claim.id,
            "claim_number": claim.claim_number,
            "claimant_name": get_claimant_name(claim) or "Unknown",
            "provider_name": getattr(claim, 'provider_name', None),
            "date_of_incident": claim.service_date.isoformat() if claim.service_date else None,
            "total_amount": float(claim.total_amount),
            "currency": claim.currency,
            "claim_type": claim.category.value if claim.category and hasattr(claim.category, 'value') else (str(claim.category) if claim.category else 'other'),
            "description": claim.description,
            "status": claim.status.value if hasattr(claim.status, 'value') else str(claim.status),
            "extracted_fields": {
                field.field_name: {
                    "value": field.value,
                    "confidence": field.confidence
                }
                for field in (claim.extracted_fields or [])
            } if hasattr(claim, 'extracted_fields') and claim.extracted_fields else {}
        }
        
        # Process through role-playing coordinator
        result = coordinator.process(
            claim_data,
            enable_discussion=request.enable_discussion,
            max_turns=request.max_turns
        )
        
        # Extract results
        review = result.get("review", {})
        decision = result.get("final_decision", {})
        discussion = None
        
        # Extract discussion if available
        for step in result.get("steps", []):
            if step.get("step") == "discussion":
                discussion = {
                    "turns": step.get("turns", 0),
                    "log": step.get("log", [])
                }
                break
        
        # Extract reasoning traces
        reasoning_traces = {}
        for step in result.get("steps", []):
            step_result = step.get("result", {})
            if step_result.get("reasoning"):
                reasoning_traces[step.get("step", "unknown")] = step_result["reasoning"]
        
        return RolePlayingReviewResponse(
            claim_id=claim.id,
            review=review,
            discussion=discussion,
            decision=decision,
            reasoning_traces=reasoning_traces
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Role-playing review failed: {str(e)}"
        )


@router.post("/{claim_id}/role-playing-approve")
async def role_playing_approve(
    claim_id: str,
    request: RolePlayingReviewRequest,
    current_user = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """
    Review and automatically approve/deny a claim using role-playing agents
    
    This performs the full role-playing review and then creates a decision record
    based on the approval agent's decision.
    """
    # Get claim
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Perform role-playing review
    review_response = await role_playing_review(claim_id, request, current_user, db)
    
    # Extract decision
    decision_data = review_response.decision.get("decision", {})
    decision_type_str = decision_data.get("decision", "pend").lower()
    
    # Map to DecisionType enum
    decision_type_map = {
        "approve": DecisionType.APPROVED,
        "deny": DecisionType.DENIED,
        "pend": DecisionType.PENDED
    }
    decision_type = decision_type_map.get(decision_type_str, DecisionType.PENDED)
    
    # Create decision record
    from backend.database.models import Decision
    decision = Decision(
        claim_id=claim_id,
        decided_by_user_id=current_user.id,
        decision=decision_type,
        reason_description=decision_data.get("reasoning", "Role-playing agent decision"),
        approved_amount=decision_data.get("approved_amount"),
        is_auto_decision=True,
        notes=f"Role-playing review with discussion: {request.enable_discussion}"
    )
    db.add(decision)
    
    # Update claim status
    if decision_type == DecisionType.APPROVED:
        claim.status = ClaimStatus.APPROVED
        claim.approved_amount = decision_data.get("approved_amount") or claim.total_amount
    elif decision_type == DecisionType.DENIED:
        claim.status = ClaimStatus.DENIED
    elif decision_type == DecisionType.PENDED:
        claim.status = ClaimStatus.PENDED
    
    claim.processed_at = datetime.utcnow()
    claim.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(decision)
    
    return {
        "message": "Claim reviewed and decision made using role-playing agents",
        "decision_id": decision.id,
        "decision": decision_type.value,
        "review": review_response.review,
        "reasoning": decision_data.get("reasoning")
    }
