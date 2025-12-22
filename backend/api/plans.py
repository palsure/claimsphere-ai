"""Plans and Insurance Companies API routes"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.database.config import get_db
from backend.database.models import (
    User, InsuranceCompany, Plan, MemberPolicy,
    RoleType, PolicyStatus
)
from backend.auth.dependencies import get_current_user, require_roles, require_any_role
from backend.api.schemas import (
    InsuranceCompanyCreate, InsuranceCompanyUpdate, InsuranceCompanyResponse,
    PlanCreate, PlanUpdate, PlanResponse,
    MemberPolicyCreate, MemberPolicyResponse
)
from backend.services.audit_service import AuditService

router = APIRouter()


# ============ Insurance Companies ============

@router.get("/companies", response_model=List[InsuranceCompanyResponse])
async def list_insurance_companies(
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all insurance companies"""
    query = db.query(InsuranceCompany)
    
    if is_active is not None:
        query = query.filter(InsuranceCompany.is_active == is_active)
    
    return query.order_by(InsuranceCompany.name).all()


@router.post("/companies", response_model=InsuranceCompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_insurance_company(
    data: InsuranceCompanyCreate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Create a new insurance company (ADMIN only)"""
    # Check for duplicate name
    existing = db.query(InsuranceCompany).filter(
        InsuranceCompany.name == data.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company with this name already exists")
    
    company = InsuranceCompany(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    
    AuditService.log(
        db, "insurance_company", company.id, "create",
        actor_user_id=current_user.id,
        after_json={"name": company.name}
    )
    
    return company


@router.put("/companies/{company_id}", response_model=InsuranceCompanyResponse)
async def update_insurance_company(
    company_id: str,
    data: InsuranceCompanyUpdate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update an insurance company (ADMIN only)"""
    company = db.query(InsuranceCompany).filter(InsuranceCompany.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(company, key, value)
    
    company.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(company)
    
    AuditService.log(
        db, "insurance_company", company.id, "update",
        actor_user_id=current_user.id,
        after_json=update_data
    )
    
    return company


# ============ Plans ============

@router.get("", response_model=List[PlanResponse])
async def list_plans(
    company_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all plans"""
    query = db.query(Plan)
    
    if company_id:
        query = query.filter(Plan.insurance_company_id == company_id)
    
    if is_active is not None:
        query = query.filter(Plan.is_active == is_active)
    
    return query.order_by(Plan.name).all()


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: PlanCreate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Create a new plan (ADMIN only)"""
    # Verify insurance company exists
    company = db.query(InsuranceCompany).filter(
        InsuranceCompany.id == data.insurance_company_id
    ).first()
    if not company:
        raise HTTPException(status_code=400, detail="Insurance company not found")
    
    plan = Plan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    AuditService.log(
        db, "plan", plan.id, "create",
        actor_user_id=current_user.id,
        after_json={"name": plan.name, "auto_approve_enabled": plan.auto_approve_enabled}
    )
    
    return plan


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get plan details"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: str,
    data: PlanUpdate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update a plan (ADMIN only)"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    before_state = {
        "auto_approve_enabled": plan.auto_approve_enabled,
        "auto_approve_amount_cap": plan.auto_approve_amount_cap
    }
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(plan, key, value)
    
    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    
    AuditService.log(
        db, "plan", plan.id, "update",
        actor_user_id=current_user.id,
        before_json=before_state,
        after_json=update_data
    )
    
    return plan


@router.delete("/{plan_id}")
async def deactivate_plan(
    plan_id: str,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Deactivate a plan (ADMIN only)"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    plan.is_active = False
    plan.updated_at = datetime.utcnow()
    db.commit()
    
    AuditService.log(
        db, "plan", plan.id, "deactivate",
        actor_user_id=current_user.id
    )
    
    return {"message": "Plan deactivated"}


# ============ Member Policies ============

@router.get("/policies/my", response_model=List[MemberPolicyResponse])
async def get_my_policies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's policies"""
    return db.query(MemberPolicy).filter(
        MemberPolicy.user_id == current_user.id
    ).all()


@router.get("/policies/{user_id}", response_model=List[MemberPolicyResponse])
async def get_user_policies(
    user_id: str,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get policies for a specific user (AGENT/ADMIN only)"""
    return db.query(MemberPolicy).filter(
        MemberPolicy.user_id == user_id
    ).all()


@router.post("/policies", response_model=MemberPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_member_policy(
    data: MemberPolicyCreate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Create a new member policy (ADMIN only)"""
    # Verify user and plan exist
    from backend.database.models import User as UserModel
    user = db.query(UserModel).filter(UserModel.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    plan = db.query(Plan).filter(Plan.id == data.plan_id).first()
    if not plan:
        raise HTTPException(status_code=400, detail="Plan not found")
    
    policy = MemberPolicy(**data.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    
    AuditService.log(
        db, "member_policy", policy.id, "create",
        actor_user_id=current_user.id,
        after_json={"user_id": data.user_id, "plan_id": data.plan_id, "member_id": data.member_id}
    )
    
    return policy

