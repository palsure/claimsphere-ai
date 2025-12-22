"""Pydantic schemas for authentication"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

from backend.database.models import RoleType


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """Registration request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response schema"""
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    roles: List[str]
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User creation schema (admin use)"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    roles: List[RoleType] = [RoleType.USER]


class UserUpdate(BaseModel):
    """User update schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str = Field(..., min_length=8)


class RoleAssignment(BaseModel):
    """Role assignment schema"""
    user_id: str
    role: RoleType


# Update forward references
TokenResponse.model_rebuild()

