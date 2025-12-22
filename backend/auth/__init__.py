"""Authentication and authorization module"""
from .service import AuthService
from .dependencies import get_current_user, require_roles, require_any_role
from .schemas import (
    TokenResponse, LoginRequest, RegisterRequest,
    UserResponse, UserCreate, UserUpdate
)

__all__ = [
    "AuthService",
    "get_current_user", "require_roles", "require_any_role",
    "TokenResponse", "LoginRequest", "RegisterRequest",
    "UserResponse", "UserCreate", "UserUpdate"
]

