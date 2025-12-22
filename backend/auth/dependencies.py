"""Authentication dependencies for FastAPI"""
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.database.config import get_db
from backend.database.models import User, RoleType
from .service import AuthService

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    if payload is None:
        raise credentials_exception

    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise return None"""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = AuthService.decode_token(token)
        
        if payload is None or payload.get("type") != "access":
            return None
        
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        
        user = AuthService.get_user_by_id(db, user_id)
        if user is None or not user.is_active:
            return None
        
        return user
    except Exception:
        return None


def require_roles(required_roles: List[RoleType]):
    """
    Dependency that requires the user to have ALL specified roles.
    
    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_roles([RoleType.ADMIN]))])
    """
    async def check_roles(user: User = Depends(get_current_user)) -> User:
        user_role_names = [ur.role.name for ur in user.roles]
        
        for role in required_roles:
            if role not in user_role_names:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required role: {role.value}"
                )
        
        return user
    
    return check_roles


def require_any_role(required_roles: List[RoleType]):
    """
    Dependency that requires the user to have ANY of the specified roles.
    
    Usage:
        @router.get("/staff-area", dependencies=[Depends(require_any_role([RoleType.AGENT, RoleType.ADMIN]))])
    """
    async def check_any_role(user: User = Depends(get_current_user)) -> User:
        user_role_names = [ur.role.name for ur in user.roles]
        
        if not any(role in user_role_names for role in required_roles):
            role_names = ", ".join([r.value for r in required_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required one of: {role_names}"
            )
        
        return user
    
    return check_any_role


class RoleChecker:
    """
    Class-based dependency for role checking with more flexibility.
    
    Usage:
        role_checker = RoleChecker([RoleType.ADMIN])
        @router.get("/admin", dependencies=[Depends(role_checker)])
    """
    def __init__(self, required_roles: List[RoleType], require_all: bool = False):
        self.required_roles = required_roles
        self.require_all = require_all

    async def __call__(self, user: User = Depends(get_current_user)) -> User:
        user_role_names = [ur.role.name for ur in user.roles]
        
        if self.require_all:
            # User must have ALL roles
            for role in self.required_roles:
                if role not in user_role_names:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Missing required role: {role.value}"
                    )
        else:
            # User must have ANY role
            if not any(role in user_role_names for role in self.required_roles):
                role_names = ", ".join([r.value for r in self.required_roles])
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required one of: {role_names}"
                )
        
        return user

