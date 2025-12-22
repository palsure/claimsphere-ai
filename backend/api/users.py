"""Users API routes"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.database.config import get_db
from backend.database.models import User, Role, UserRole, RoleType
from backend.auth.service import AuthService
from backend.auth.schemas import UserResponse, UserCreate, UserUpdate, RoleAssignment
from backend.auth.dependencies import get_current_user, require_roles, require_any_role
from backend.services.audit_service import AuditService

router = APIRouter()


def user_to_response(user: User) -> UserResponse:
    """Convert User model to UserResponse"""
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        is_active=user.is_active,
        is_verified=user.is_verified,
        roles=[ur.role.name.value for ur in user.roles],
        created_at=user.created_at,
        last_login=user.last_login
    )


@router.get("", response_model=List[UserResponse])
async def list_users(
    role: Optional[RoleType] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """List all users (ADMIN only)"""
    query = db.query(User)
    
    if role:
        query = query.join(UserRole).join(Role).filter(Role.name == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.email.ilike(search_term)) |
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term))
        )
    
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    users = query.all()
    return [user_to_response(u) for u in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Create a new user (ADMIN only)"""
    try:
        user = AuthService.create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            roles=user_data.roles
        )
        
        AuditService.log(
            db, "user", user.id, "create",
            actor_user_id=current_user.id,
            after_json={"email": user.email, "roles": [r.value for r in user_data.roles]}
        )
        
        return user_to_response(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Get user by ID (ADMIN only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_response(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Update a user (ADMIN only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    before_state = {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": user.is_active
    }
    
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    AuditService.log(
        db, "user", user.id, "update",
        actor_user_id=current_user.id,
        before_json=before_state,
        after_json={
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active
        }
    )
    
    return user_to_response(user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Deactivate a user (ADMIN only)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()
    
    AuditService.log(
        db, "user", user.id, "deactivate",
        actor_user_id=current_user.id
    )
    
    return {"message": "User deactivated"}


@router.post("/{user_id}/roles")
async def assign_user_role(
    user_id: str,
    role: RoleType,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Assign a role to a user (ADMIN only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    AuthService.assign_role(db, user_id, role, current_user.id)
    
    AuditService.log(
        db, "user", user.id, "assign_role",
        actor_user_id=current_user.id,
        after_json={"role": role.value}
    )
    
    return {"message": f"Role {role.value} assigned to user"}


@router.delete("/{user_id}/roles/{role}")
async def remove_user_role(
    user_id: str,
    role: RoleType,
    current_user: User = Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN])),
    db: Session = Depends(get_db)
):
    """Remove a role from a user (ADMIN only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't allow removing the last role
    if len(user.roles) <= 1:
        raise HTTPException(status_code=400, detail="Cannot remove the last role")
    
    AuthService.remove_role(db, user_id, role)
    
    AuditService.log(
        db, "user", user.id, "remove_role",
        actor_user_id=current_user.id,
        after_json={"role_removed": role.value}
    )
    
    return {"message": f"Role {role.value} removed from user"}

