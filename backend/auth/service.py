"""Authentication service with JWT and password hashing"""
import os
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from backend.database.models import User, Role, UserRole, RoleType

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class AuthService:
    """Service for authentication and authorization"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "type": "access"
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and validate a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password"""
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        roles: List[RoleType] = None
    ) -> User:
        """Create a new user"""
        # Check if user exists
        if AuthService.get_user_by_email(db, email):
            raise ValueError("User with this email already exists")

        # Create user
        user = User(
            email=email,
            hashed_password=AuthService.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        db.add(user)
        db.flush()  # Get the user ID

        # Assign roles (default to USER if none specified)
        if not roles:
            roles = [RoleType.USER]

        for role_type in roles:
            role = db.query(Role).filter(Role.name == role_type).first()
            if not role:
                # Create role if it doesn't exist
                role = Role(name=role_type)
                db.add(role)
                db.flush()

            user_role = UserRole(user_id=user.id, role_id=role.id)
            db.add(user_role)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def assign_role(db: Session, user_id: str, role_type: RoleType, assigned_by_id: Optional[str] = None) -> UserRole:
        """Assign a role to a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        role = db.query(Role).filter(Role.name == role_type).first()
        if not role:
            role = Role(name=role_type)
            db.add(role)
            db.flush()

        # Check if already assigned
        existing = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role.id
        ).first()
        
        if existing:
            return existing

        user_role = UserRole(
            user_id=user_id,
            role_id=role.id,
            assigned_by_id=assigned_by_id
        )
        db.add(user_role)
        db.commit()
        return user_role

    @staticmethod
    def remove_role(db: Session, user_id: str, role_type: RoleType) -> bool:
        """Remove a role from a user"""
        role = db.query(Role).filter(Role.name == role_type).first()
        if not role:
            return False

        user_role = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role.id
        ).first()

        if user_role:
            db.delete(user_role)
            db.commit()
            return True
        return False

    @staticmethod
    def user_has_role(user: User, role_type: RoleType) -> bool:
        """Check if a user has a specific role"""
        return role_type.value in [ur.role.name.value for ur in user.roles]

    @staticmethod
    def user_has_any_role(user: User, role_types: List[RoleType]) -> bool:
        """Check if a user has any of the specified roles"""
        user_roles = [ur.role.name for ur in user.roles]
        return any(role in user_roles for role in role_types)

    @staticmethod
    def init_default_roles(db: Session):
        """Initialize default roles in the database"""
        for role_type in RoleType:
            existing = db.query(Role).filter(Role.name == role_type).first()
            if not existing:
                permissions = AuthService._get_default_permissions(role_type)
                role = Role(
                    name=role_type,
                    description=f"Default {role_type.value} role",
                    permissions=permissions
                )
                db.add(role)
        db.commit()

    @staticmethod
    def _get_default_permissions(role_type: RoleType) -> List[str]:
        """Get default permissions for a role type"""
        base_permissions = ["profile:read", "profile:update"]
        
        if role_type == RoleType.USER:
            return base_permissions + [
                "claims:create", "claims:read:own", "claims:update:own",
                "claims:correct:own", "query:own"
            ]
        elif role_type == RoleType.AGENT:
            return base_permissions + [
                "claims:read:assigned", "claims:review", "claims:decide",
                "claims:request_info", "duplicates:view", "query:assigned"
            ]
        elif role_type == RoleType.ADMIN:
            return base_permissions + [
                "users:manage", "roles:manage",
                "plans:manage", "rules:manage", "thresholds:manage",
                "claims:read:all", "analytics:view", "audit:view",
                "query:all"
            ]
        return base_permissions

