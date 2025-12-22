"""Claims API routes"""
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.database.config import get_db
from backend.database.models import (
    User, Claim, ClaimDocument, ExtractedField, Decision,
    ValidationResult, DuplicateMatch, AuditLog,
    ClaimStatus, ClaimCategory, DecisionType, FieldSource, RoleType
)
from backend.auth.dependencies import get_current_user, require_any_role
from backend.api.schemas import (
    ClaimCreate, ClaimUpdate, ClaimResponse, ClaimListResponse,
    ClaimStatusUpdate, ExtractedFieldCorrection, DecisionCreate,
    DecisionResponse, DuplicateMatchResponse
)
from backend.services.claim_service import ClaimService
from backend.services.audit_service import AuditService

router = APIRouter()


def get_claimant_name(claim: Claim) -> Optional[str]:
    """Get claimant name from extracted fields"""
    if claim.extracted_fields:
        for field in claim.extracted_fields:
            if field.field_name == 'claimant_name' and field.value:
                return field.value
    return None


def claim_to_list_response(claim: Claim) -> ClaimListResponse:
    """Convert Claim model to ClaimListResponse with extracted fields"""
    return ClaimListResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        user_id=claim.user_id,
        claimant_name=get_claimant_name(claim),
        status=claim.status,
        category=claim.category,
        total_amount=claim.total_amount,
        approved_amount=claim.approved_amount,
        currency=claim.currency,
        service_date=claim.service_date,
        provider_name=claim.provider_name,
        created_at=claim.created_at,
        submitted_at=claim.submitted_at,
        is_duplicate=claim.duplicate_score > 0.7,
        duplicate_score=claim.duplicate_score
    )


def claim_to_response(claim: Claim, include_details: bool = True) -> ClaimResponse:
    """Convert Claim model to ClaimResponse"""
    response = ClaimResponse(
        id=claim.id,
        claim_number=claim.claim_number,
        user_id=claim.user_id,
        claimant_name=get_claimant_name(claim),
        plan_id=claim.plan_id,
        assigned_agent_id=claim.assigned_agent_id,
        status=claim.status,
        category=claim.category,
        total_amount=claim.total_amount,
        approved_amount=claim.approved_amount,
        currency=claim.currency,
        service_date=claim.service_date,
        provider_name=claim.provider_name,
        description=claim.description,
        ocr_quality_score=claim.ocr_quality_score,
        extraction_confidence=claim.extraction_confidence,
        duplicate_score=claim.duplicate_score,
        fraud_risk_score=claim.fraud_risk_score,
        is_duplicate=claim.duplicate_score > 0.6,
        auto_approval_eligible=claim.auto_approval_eligible,
        created_at=claim.created_at,
        submitted_at=claim.submitted_at,
        documents=[],
        extracted_fields=[],
        validation_results=[],
        decisions=[],
        duplicate_matches=[]
    )
    
    if include_details:
        response.documents = claim.documents
        response.extracted_fields = claim.extracted_fields
        response.validation_results = claim.validation_results
        response.decisions = claim.decisions
        response.duplicate_matches = claim.duplicate_matches
    
    return response


# ============ User Endpoints (Submit, View Own, Correct) ============

@router.post("", response_model=ClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_claim(
    claim_data: ClaimCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new claim (USER role)"""
    claim = ClaimService.create_claim(db, current_user.id, claim_data)
    AuditService.log(
        db, "claim", claim.id, "create",
        actor_user_id=current_user.id,
        after_json={"claim_number": claim.claim_number, "status": claim.status.value}
    )
    return claim_to_response(claim)


@router.post("/upload")
async def upload_and_create_claim(
    file: UploadFile = File(...),
    process_with_ai: bool = Query(True, description="Process with AI to extract claim info"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document and create a new claim from it.
    The document will be processed with OCR and AI to extract claim information.
    """
    # Validate file type
    allowed_types = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} not allowed. Allowed: PDF, JPEG, PNG, GIF"
        )
    
    # Create claim and process document
    claim = await ClaimService.create_claim_from_document(
        db=db,
        user_id=current_user.id,
        file=file,
        process_with_ai=process_with_ai
    )
    
    AuditService.log(
        db, "claim", claim.id, "create_from_upload",
        actor_user_id=current_user.id,
        after_json={"claim_number": claim.claim_number, "status": claim.status.value}
    )
    
    return {
        "message": "Claim created successfully",
        "claim": claim_to_response(claim)
    }


@router.get("/analytics")
async def get_claims_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for claims based on user role"""
    from sqlalchemy import func
    from collections import defaultdict
    from datetime import timedelta
    
    user_roles = [ur.role.name for ur in current_user.roles]
    
    # Build base query based on role
    query = db.query(Claim)
    if RoleType.ADMIN not in user_roles and RoleType.AGENT not in user_roles:
        query = query.filter(Claim.user_id == current_user.id)
    
    claims = query.all()
    
    if not claims:
        return {
            "total_claims": 0,
            "total_amount": 0.0,
            "approved_amount": 0.0,
            "pending_amount": 0.0,
            "approval_rate": 0.0,
            "average_processing_time": 0.0,
            "type_breakdown": {},
            "status_breakdown": {},
            "monthly_trends": [],
            "top_claimants": []
        }
    
    # Calculate totals
    total_amount = sum(c.total_amount or 0 for c in claims)
    approved_claims = [c for c in claims if c.status in [ClaimStatus.APPROVED, ClaimStatus.AUTO_APPROVED]]
    approved_amount = sum(c.approved_amount or c.total_amount or 0 for c in approved_claims)
    pending_claims = [c for c in claims if c.status in [ClaimStatus.SUBMITTED, ClaimStatus.EXTRACTED, ClaimStatus.VALIDATED, ClaimStatus.PENDING_REVIEW, ClaimStatus.PENDED]]
    pending_amount = sum(c.total_amount or 0 for c in pending_claims)
    
    # Approval rate
    completed_claims = [c for c in claims if c.status in [ClaimStatus.APPROVED, ClaimStatus.AUTO_APPROVED, ClaimStatus.DENIED]]
    approval_rate = (len(approved_claims) / len(completed_claims) * 100) if completed_claims else 0
    
    # Average processing time
    processing_times = []
    for c in completed_claims:
        if c.submitted_at and c.processed_at:
            delta = (c.processed_at - c.submitted_at).total_seconds() / 86400  # days
            processing_times.append(delta)
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    # Category breakdown
    category_breakdown = defaultdict(int)
    for c in claims:
        category_breakdown[c.category.value] += 1
    
    # Status breakdown
    status_breakdown = defaultdict(int)
    for c in claims:
        status_breakdown[c.status.value] += 1
    
    # Monthly trends (last 6 months)
    from datetime import datetime
    monthly_trends = []
    now = datetime.utcnow()
    for i in range(5, -1, -1):
        month_start = now.replace(day=1) - timedelta(days=i*30)
        month_name = month_start.strftime("%b %Y")
        month_claims = [c for c in claims if c.created_at and c.created_at.month == month_start.month and c.created_at.year == month_start.year]
        monthly_trends.append({
            "month": month_name,
            "count": len(month_claims),
            "total": sum(c.total_amount or 0 for c in month_claims)
        })
    
    # Top claimants (from extracted fields)
    claimant_totals = defaultdict(lambda: {"count": 0, "total": 0.0})
    for c in claims:
        claimant_name = get_claimant_name(c) or "Unknown"
        claimant_totals[claimant_name]["count"] += 1
        claimant_totals[claimant_name]["total"] += c.total_amount or 0
    
    top_claimants = [
        {"claimant": name, "count": data["count"], "total": data["total"]}
        for name, data in sorted(claimant_totals.items(), key=lambda x: x[1]["total"], reverse=True)[:10]
    ]
    
    return {
        "total_claims": len(claims),
        "total_amount": total_amount,
        "approved_amount": approved_amount,
        "pending_amount": pending_amount,
        "approval_rate": approval_rate,
        "average_processing_time": avg_processing_time,
        "type_breakdown": dict(category_breakdown),
        "status_breakdown": dict(status_breakdown),
        "monthly_trends": monthly_trends,
        "top_claimants": top_claimants
    }


@router.get("", response_model=List[ClaimListResponse])
async def list_claims(
    status: Optional[ClaimStatus] = None,
    category: Optional[ClaimCategory] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List claims based on user role:
    - USER: Only own claims
    - AGENT: Assigned claims or pending review
    - ADMIN: All claims
    """
    user_roles = [ur.role.name for ur in current_user.roles]
    
    query = db.query(Claim)
    
    if RoleType.ADMIN in user_roles:
        # Admin sees all claims
        pass
    elif RoleType.AGENT in user_roles:
        # Agent sees assigned claims or pending review
        query = query.filter(
            or_(
                Claim.assigned_agent_id == current_user.id,
                Claim.status == ClaimStatus.PENDING_REVIEW
            )
        )
    else:
        # User sees only own claims
        query = query.filter(Claim.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(Claim.status == status)
    if category:
        query = query.filter(Claim.category == category)
    if date_from:
        query = query.filter(Claim.created_at >= date_from)
    if date_to:
        query = query.filter(Claim.created_at <= date_to)
    
    # Pagination
    query = query.order_by(Claim.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    claims = query.all()
    return [claim_to_list_response(c) for c in claims]


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(
    claim_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get claim details (with role-based access)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Check access
    user_roles = [ur.role.name for ur in current_user.roles]
    
    if RoleType.ADMIN not in user_roles:
        if RoleType.AGENT in user_roles:
            if claim.assigned_agent_id != current_user.id and claim.status != ClaimStatus.PENDING_REVIEW:
                raise HTTPException(status_code=403, detail="Not authorized to view this claim")
        else:
            if claim.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized to view this claim")
    
    return claim_to_response(claim)


@router.put("/{claim_id}", response_model=ClaimResponse)
async def update_claim(
    claim_id: str,
    claim_data: ClaimUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update claim (only owner, only in DRAFT status)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this claim")
    
    if claim.status != ClaimStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Can only update claims in DRAFT status")
    
    before_state = {"status": claim.status.value, "total_amount": claim.total_amount}


@router.delete("/{claim_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_claim(
    claim_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete claim (only owner, only in DRAFT/SUBMITTED status, or ADMIN can delete any)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    user_roles = [ur.role.name for ur in current_user.roles]
    is_admin = RoleType.ADMIN in user_roles
    
    # Check ownership or admin access
    if not is_admin and claim.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this claim")
    
    # Only allow deletion of draft/submitted claims (unless admin)
    deletable_statuses = [ClaimStatus.DRAFT, ClaimStatus.SUBMITTED, ClaimStatus.EXTRACTED]
    if not is_admin and claim.status not in deletable_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete claim in {claim.status.value} status. Only DRAFT, SUBMITTED, or EXTRACTED claims can be deleted."
        )
    
    # Log the deletion
    AuditService.log(
        db, "claim", claim.id, "delete",
        actor_user_id=current_user.id,
        before_json={"claim_number": claim.claim_number, "status": claim.status.value}
    )
    
    # Delete related records first (cascade should handle but explicit is safer)
    from backend.database.models import ClaimDocument, ExtractedField, ValidationResult, DuplicateMatch
    
    db.query(ExtractedField).filter(ExtractedField.claim_id == claim_id).delete()
    db.query(ValidationResult).filter(ValidationResult.claim_id == claim_id).delete()
    db.query(DuplicateMatch).filter(DuplicateMatch.claim_id == claim_id).delete()
    db.query(DuplicateMatch).filter(DuplicateMatch.matched_claim_id == claim_id).delete()
    db.query(ClaimDocument).filter(ClaimDocument.claim_id == claim_id).delete()
    
    # Delete the claim
    db.delete(claim)
    db.commit()
    
    return None
    
    # Update fields
    update_data = claim_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(claim, key, value)
    
    claim.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(claim)
    
    AuditService.log(
        db, "claim", claim.id, "update",
        actor_user_id=current_user.id,
        before_json=before_state,
        after_json={"status": claim.status.value, "total_amount": claim.total_amount}
    )
    
    return claim_to_response(claim)


@router.post("/{claim_id}/submit", response_model=ClaimResponse)
async def submit_claim(
    claim_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a draft claim for processing"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if claim.status != ClaimStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Claim is not in DRAFT status")
    
    # Transition to SUBMITTED
    claim = ClaimService.transition_status(
        db, claim, ClaimStatus.SUBMITTED, current_user.id
    )
    
    return claim_to_response(claim)


@router.post("/{claim_id}/upload", response_model=ClaimResponse)
async def upload_claim_document(
    claim_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document for a claim"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    if claim.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if claim.status not in [ClaimStatus.DRAFT, ClaimStatus.SUBMITTED]:
        raise HTTPException(status_code=400, detail="Cannot upload documents to this claim")
    
    # Process document
    claim = await ClaimService.add_document(db, claim, file, current_user.id)
    
    return claim_to_response(claim)


@router.post("/{claim_id}/correct-field")
async def correct_extracted_field(
    claim_id: str,
    correction: ExtractedFieldCorrection,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Correct an extracted field (user can correct own claims)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Check authorization
    user_roles = [ur.role.name for ur in current_user.roles]
    
    if claim.user_id != current_user.id and RoleType.AGENT not in user_roles and RoleType.ADMIN not in user_roles:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Find or create the field
    field = db.query(ExtractedField).filter(
        ExtractedField.claim_id == claim_id,
        ExtractedField.field_name == correction.field_name
    ).first()
    
    if field:
        # Store original value
        if not field.original_value:
            field.original_value = field.value
        field.value = correction.value
        field.source = FieldSource.USER if claim.user_id == current_user.id else FieldSource.AGENT
        field.corrected_by = current_user.id
        field.corrected_at = datetime.utcnow()
    else:
        field = ExtractedField(
            claim_id=claim_id,
            field_name=correction.field_name,
            value=correction.value,
            source=FieldSource.USER if claim.user_id == current_user.id else FieldSource.AGENT,
            corrected_by=current_user.id,
            corrected_at=datetime.utcnow()
        )
        db.add(field)
    
    db.commit()
    
    AuditService.log(
        db, "extracted_field", field.id, "correct",
        actor_user_id=current_user.id,
        after_json={"field_name": correction.field_name, "value": correction.value}
    )
    
    return {"message": "Field corrected", "field_name": correction.field_name}


# ============ Agent Endpoints (Review, Decide) ============

@router.get("/queue/pending", response_model=List[ClaimListResponse])
async def get_agent_queue(
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get claims pending review (AGENT/ADMIN only)"""
    claims = db.query(Claim).filter(
        Claim.status == ClaimStatus.PENDING_REVIEW
    ).order_by(Claim.created_at.asc()).all()
    
    return [claim_to_list_response(c) for c in claims]


@router.post("/{claim_id}/assign")
async def assign_claim_to_agent(
    claim_id: str,
    agent_id: Optional[str] = None,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Assign a claim to an agent (or self-assign)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    target_agent_id = agent_id or current_user.id
    
    claim.assigned_agent_id = target_agent_id
    claim.updated_at = datetime.utcnow()
    db.commit()
    
    AuditService.log(
        db, "claim", claim.id, "assign",
        actor_user_id=current_user.id,
        after_json={"assigned_agent_id": target_agent_id}
    )
    
    return {"message": "Claim assigned", "agent_id": target_agent_id}


@router.post("/{claim_id}/decide", response_model=DecisionResponse)
async def make_decision(
    claim_id: str,
    decision_data: DecisionCreate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Make a decision on a claim (approve/deny/pend)"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # Allow decisions on these statuses
    actionable_statuses = [
        ClaimStatus.SUBMITTED, 
        ClaimStatus.EXTRACTED, 
        ClaimStatus.VALIDATED, 
        ClaimStatus.PENDING_REVIEW,
        ClaimStatus.PENDED
    ]
    if claim.status not in actionable_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Claim is not ready for decision. Current status: {claim.status.value}. Allowed statuses: {[s.value for s in actionable_statuses]}"
        )
    
    # Create decision record
    decision = Decision(
        claim_id=claim_id,
        decided_by_user_id=current_user.id,
        decision=decision_data.decision,
        reason_code=decision_data.reason_code,
        reason_description=decision_data.reason_description,
        notes=decision_data.notes,
        approved_amount=decision_data.approved_amount,
        is_auto_decision=False
    )
    db.add(decision)
    
    # Update claim status based on decision
    if decision_data.decision == DecisionType.APPROVED:
        claim.status = ClaimStatus.APPROVED
        claim.approved_amount = decision_data.approved_amount or claim.total_amount
    elif decision_data.decision == DecisionType.DENIED:
        claim.status = ClaimStatus.DENIED
    elif decision_data.decision == DecisionType.PENDED:
        claim.status = ClaimStatus.PENDED
    
    claim.processed_at = datetime.utcnow()
    claim.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(decision)
    
    AuditService.log(
        db, "claim", claim.id, "decision",
        actor_user_id=current_user.id,
        after_json={
            "decision": decision_data.decision.value,
            "status": claim.status.value,
            "approved_amount": claim.approved_amount
        }
    )
    
    return DecisionResponse(
        id=decision.id,
        decision=decision.decision,
        reason_code=decision.reason_code,
        reason_description=decision.reason_description,
        notes=decision.notes,
        approved_amount=decision.approved_amount,
        is_auto_decision=decision.is_auto_decision,
        decided_by_name=current_user.full_name,
        created_at=decision.created_at
    )


@router.post("/{claim_id}/request-info")
async def request_additional_info(
    claim_id: str,
    message: str,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Request additional information from claimant"""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    claim.status = ClaimStatus.PENDED
    claim.updated_at = datetime.utcnow()
    
    # Add a decision record for tracking
    decision = Decision(
        claim_id=claim_id,
        decided_by_user_id=current_user.id,
        decision=DecisionType.PENDED,
        reason_code="INFO_REQUIRED",
        notes=message,
        is_auto_decision=False
    )
    db.add(decision)
    db.commit()
    
    AuditService.log(
        db, "claim", claim.id, "request_info",
        actor_user_id=current_user.id,
        after_json={"status": "pended", "message": message}
    )
    
    return {"message": "Information request sent", "claim_status": "pended"}


@router.get("/{claim_id}/duplicates", response_model=List[DuplicateMatchResponse])
async def get_claim_duplicates(
    claim_id: str,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get potential duplicate claims"""
    matches = db.query(DuplicateMatch).filter(
        DuplicateMatch.claim_id == claim_id
    ).all()
    
    result = []
    for match in matches:
        matched_claim = db.query(Claim).filter(Claim.id == match.matched_claim_id).first()
        result.append(DuplicateMatchResponse(
            id=match.id,
            matched_claim_id=match.matched_claim_id,
            matched_claim_number=matched_claim.claim_number if matched_claim else None,
            similarity_score=match.similarity_score,
            match_reasons_json=match.match_reasons_json,
            is_confirmed_duplicate=match.is_confirmed_duplicate
        ))
    
    return result

