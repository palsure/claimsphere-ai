"""Validation Rules API routes"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.config import get_db
from backend.database.models import User, ValidationRule, RoleType
from backend.auth.dependencies import get_current_user, require_roles, require_any_role
from backend.api.schemas import (
    ValidationRuleCreate, ValidationRuleUpdate, ValidationRuleResponse
)
from backend.services.audit_service import AuditService

router = APIRouter()


@router.get("/rules", response_model=List[ValidationRuleResponse])
async def list_validation_rules(
    plan_id: Optional[str] = None,
    rule_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """List all validation rules (ADMIN only)"""
    query = db.query(ValidationRule)
    
    if plan_id:
        query = query.filter(ValidationRule.plan_id == plan_id)
    
    if rule_type:
        query = query.filter(ValidationRule.rule_type == rule_type)
    
    if is_active is not None:
        query = query.filter(ValidationRule.is_active == is_active)
    
    return query.order_by(ValidationRule.order, ValidationRule.name).all()


@router.post("/rules", response_model=ValidationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_validation_rule(
    data: ValidationRuleCreate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Create a new validation rule (ADMIN only)"""
    rule = ValidationRule(**data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    AuditService.log(
        db, "validation_rule", rule.id, "create",
        actor_user_id=current_user.id,
        after_json={"name": rule.name, "rule_type": rule.rule_type}
    )
    
    return rule


@router.get("/rules/{rule_id}", response_model=ValidationRuleResponse)
async def get_validation_rule(
    rule_id: str,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get a validation rule (ADMIN only)"""
    rule = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/rules/{rule_id}", response_model=ValidationRuleResponse)
async def update_validation_rule(
    rule_id: str,
    data: ValidationRuleUpdate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update a validation rule (ADMIN only)"""
    rule = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    before_state = {
        "name": rule.name,
        "condition_json": rule.condition_json,
        "is_active": rule.is_active
    }
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)
    
    rule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rule)
    
    AuditService.log(
        db, "validation_rule", rule.id, "update",
        actor_user_id=current_user.id,
        before_json=before_state,
        after_json=update_data
    )
    
    return rule


@router.delete("/rules/{rule_id}")
async def delete_validation_rule(
    rule_id: str,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Deactivate a validation rule (ADMIN only)"""
    rule = db.query(ValidationRule).filter(ValidationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.is_active = False
    rule.updated_at = datetime.utcnow()
    db.commit()
    
    AuditService.log(
        db, "validation_rule", rule.id, "deactivate",
        actor_user_id=current_user.id
    )
    
    return {"message": "Rule deactivated"}


# ============ Rule Types Reference ============

@router.get("/rule-types")
async def get_rule_types(
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN]))
):
    """Get available validation rule types and their schemas"""
    return {
        "rule_types": [
            {
                "type": "amount_limit",
                "description": "Check if claim amount is within limits",
                "schema": {
                    "max_amount": {"type": "number", "required": True},
                    "min_amount": {"type": "number", "required": False}
                }
            },
            {
                "type": "date_range",
                "description": "Check if service date is within valid range",
                "schema": {
                    "max_days_past": {"type": "integer", "required": True},
                    "max_days_future": {"type": "integer", "required": False, "default": 0}
                }
            },
            {
                "type": "required_fields",
                "description": "Check if required fields are present",
                "schema": {
                    "fields": {"type": "array", "items": "string", "required": True}
                }
            },
            {
                "type": "required_documents",
                "description": "Check if required document types are uploaded",
                "schema": {
                    "document_types": {"type": "array", "items": "string", "required": True}
                }
            },
            {
                "type": "eligibility",
                "description": "Check member eligibility based on policy dates",
                "schema": {
                    "require_active_policy": {"type": "boolean", "default": True}
                }
            },
            {
                "type": "duplicate_check",
                "description": "Check for potential duplicate claims",
                "schema": {
                    "similarity_threshold": {"type": "number", "default": 0.85},
                    "days_window": {"type": "integer", "default": 30}
                }
            },
            {
                "type": "provider_validation",
                "description": "Validate provider information",
                "schema": {
                    "require_npi": {"type": "boolean", "default": False},
                    "allowed_provider_types": {"type": "array", "items": "string", "required": False}
                }
            },
            {
                "type": "category_rules",
                "description": "Category-specific validation rules",
                "schema": {
                    "category": {"type": "string", "required": True},
                    "max_amount": {"type": "number", "required": False},
                    "required_codes": {"type": "array", "items": "string", "required": False}
                }
            }
        ]
    }

