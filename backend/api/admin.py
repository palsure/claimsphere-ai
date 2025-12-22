"""Admin API routes"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database.config import get_db
from backend.database.models import (
    User, Claim, AuditLog, Decision,
    ClaimStatus, RoleType
)
from backend.auth.dependencies import require_roles, require_any_role
from backend.api.schemas import ClaimAnalytics, AuditLogResponse

router = APIRouter()


@router.get("/analytics", response_model=ClaimAnalytics)
async def get_claim_analytics(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get claim analytics (ADMIN only)"""
    query = db.query(Claim)
    
    if date_from:
        query = query.filter(Claim.created_at >= date_from)
    if date_to:
        query = query.filter(Claim.created_at <= date_to)
    
    claims = query.all()
    
    if not claims:
        return ClaimAnalytics(
            total_claims=0,
            total_amount=0,
            approved_amount=0,
            pending_amount=0,
            denied_amount=0,
            status_breakdown={},
            category_breakdown={},
            monthly_trends=[],
            average_processing_time_hours=0,
            auto_approval_rate=0,
            approval_rate=0
        )
    
    # Calculate metrics
    total_claims = len(claims)
    total_amount = sum(c.total_amount for c in claims)
    
    approved_claims = [c for c in claims if c.status in [ClaimStatus.APPROVED, ClaimStatus.AUTO_APPROVED]]
    approved_amount = sum(c.approved_amount or c.total_amount for c in approved_claims)
    
    pending_claims = [c for c in claims if c.status in [ClaimStatus.SUBMITTED, ClaimStatus.PENDING_REVIEW, ClaimStatus.VALIDATED]]
    pending_amount = sum(c.total_amount for c in pending_claims)
    
    denied_claims = [c for c in claims if c.status == ClaimStatus.DENIED]
    denied_amount = sum(c.total_amount for c in denied_claims)
    
    # Status breakdown
    status_breakdown = {}
    for c in claims:
        status = c.status.value
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    # Category breakdown
    category_breakdown = {}
    for c in claims:
        cat = c.category.value
        category_breakdown[cat] = category_breakdown.get(cat, 0) + 1
    
    # Monthly trends (last 6 months)
    monthly_trends = []
    now = datetime.utcnow()
    for i in range(5, -1, -1):
        month_start = (now - timedelta(days=30*i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            month_end = (now - timedelta(days=30*(i-1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            month_end = now
        
        month_claims = [c for c in claims if month_start <= c.created_at < month_end]
        month_approved = [c for c in month_claims if c.status in [ClaimStatus.APPROVED, ClaimStatus.AUTO_APPROVED]]
        
        monthly_trends.append({
            "month": month_start.strftime("%Y-%m"),
            "total_claims": len(month_claims),
            "total_amount": sum(c.total_amount for c in month_claims),
            "approved_count": len(month_approved),
            "approved_amount": sum(c.approved_amount or c.total_amount for c in month_approved)
        })
    
    # Average processing time (for processed claims)
    processed_claims = [c for c in claims if c.processed_at and c.submitted_at]
    if processed_claims:
        avg_time = sum(
            (c.processed_at - c.submitted_at).total_seconds() / 3600
            for c in processed_claims
        ) / len(processed_claims)
    else:
        avg_time = 0
    
    # Auto-approval rate
    auto_approved = [c for c in claims if c.status == ClaimStatus.AUTO_APPROVED]
    processed_count = len(approved_claims) + len(denied_claims)
    auto_approval_rate = len(auto_approved) / processed_count if processed_count > 0 else 0
    
    # Overall approval rate
    approval_rate = len(approved_claims) / processed_count if processed_count > 0 else 0
    
    return ClaimAnalytics(
        total_claims=total_claims,
        total_amount=total_amount,
        approved_amount=approved_amount,
        pending_amount=pending_amount,
        denied_amount=denied_amount,
        status_breakdown=status_breakdown,
        category_breakdown=category_breakdown,
        monthly_trends=monthly_trends,
        average_processing_time_hours=round(avg_time, 2),
        auto_approval_rate=round(auto_approval_rate * 100, 2),
        approval_rate=round(approval_rate * 100, 2)
    )


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    action: Optional[str] = None,
    actor_user_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get audit logs (ADMIN only)"""
    query = db.query(AuditLog)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if actor_user_id:
        query = query.filter(AuditLog.actor_user_id == actor_user_id)
    if date_from:
        query = query.filter(AuditLog.created_at >= date_from)
    if date_to:
        query = query.filter(AuditLog.created_at <= date_to)
    
    query = query.order_by(AuditLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    logs = query.all()
    
    # Enrich with actor names
    result = []
    for log in logs:
        actor_name = None
        if log.actor:
            actor_name = log.actor.full_name
        
        result.append(AuditLogResponse(
            id=log.id,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            action=log.action,
            actor_user_id=log.actor_user_id,
            actor_name=actor_name,
            before_json=log.before_json,
            after_json=log.after_json,
            created_at=log.created_at
        ))
    
    return result


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get quick dashboard statistics (ADMIN only)"""
    # Count users by role
    from backend.database.models import UserRole, Role
    
    total_users = db.query(User).filter(User.is_active == True).count()
    
    user_count = db.query(UserRole).join(Role).filter(Role.name == RoleType.USER).count()
    agent_count = db.query(UserRole).join(Role).filter(Role.name == RoleType.AGENT).count()
    admin_count = db.query(UserRole).join(Role).filter(Role.name == RoleType.ADMIN).count()
    
    # Claims stats
    total_claims = db.query(Claim).count()
    pending_review = db.query(Claim).filter(Claim.status == ClaimStatus.PENDING_REVIEW).count()
    today_submitted = db.query(Claim).filter(
        Claim.submitted_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    # Amount stats
    total_amount = db.query(func.sum(Claim.total_amount)).scalar() or 0
    approved_amount = db.query(func.sum(Claim.approved_amount)).filter(
        Claim.status.in_([ClaimStatus.APPROVED, ClaimStatus.AUTO_APPROVED])
    ).scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "by_role": {
                "user": user_count,
                "agent": agent_count,
                "admin": admin_count
            }
        },
        "claims": {
            "total": total_claims,
            "pending_review": pending_review,
            "submitted_today": today_submitted
        },
        "amounts": {
            "total_claimed": total_amount,
            "total_approved": approved_amount
        }
    }

