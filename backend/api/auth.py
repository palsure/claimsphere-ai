"""Authentication API routes"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.config import get_db
from backend.database.models import User, RoleType
from backend.auth.service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.auth.schemas import (
    LoginRequest, RegisterRequest, TokenResponse, 
    UserResponse, RefreshTokenRequest, PasswordChange
)
from backend.auth.dependencies import get_current_user

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


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account"""
    try:
        user = AuthService.create_user(
            db=db,
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            roles=[RoleType.USER]
        )
        
        # Create tokens
        access_token = AuthService.create_access_token(data={"sub": user.id})
        refresh_token = AuthService.create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_to_response(user)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = AuthService.authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": user.id})
    refresh_token = AuthService.create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_to_response(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    payload = AuthService.decode_token(request.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = AuthService.get_user_by_id(db, user_id)
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = AuthService.create_access_token(data={"sub": user.id})
    refresh_token = AuthService.create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_to_response(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return user_to_response(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    first_name: str = None,
    last_name: str = None,
    phone: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    if phone is not None:
        current_user.phone = phone
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return user_to_response(current_user)


@router.post("/change-password")
async def change_password(
    request: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not AuthService.verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.hashed_password = AuthService.hash_password(request.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}

