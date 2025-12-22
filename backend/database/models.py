"""SQLAlchemy database models for ClaimSphere"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .config import Base


# ============ Enums ============

class RoleType(str, PyEnum):
    USER = "user"           # Claimant - can submit and view own claims
    AGENT = "agent"         # Adjuster - can review and decide on claims
    ADMIN = "admin"         # Administrator - can manage system configuration


class ClaimStatus(str, PyEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    AUTO_APPROVED = "auto_approved"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    DENIED = "denied"
    PENDED = "pended"       # Need more info
    CLOSED = "closed"


class ClaimCategory(str, PyEnum):
    MEDICAL = "medical"
    DENTAL = "dental"
    VISION = "vision"
    PHARMACY = "pharmacy"
    MENTAL_HEALTH = "mental_health"
    HOSPITAL = "hospital"
    EMERGENCY = "emergency"
    PREVENTIVE = "preventive"
    OTHER = "other"


class DecisionType(str, PyEnum):
    APPROVED = "approved"
    DENIED = "denied"
    PENDED = "pended"
    ESCALATED = "escalated"


class PolicyStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class FieldSource(str, PyEnum):
    OCR = "ocr"
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


# ============ Helper for UUID ============

def generate_uuid():
    return str(uuid.uuid4())


# ============ User & Role Models ============

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    policies = relationship("MemberPolicy", back_populates="user")
    claims = relationship("Claim", back_populates="user", foreign_keys="Claim.user_id")
    decisions = relationship("Decision", back_populates="decided_by")
    audit_logs = relationship("AuditLog", back_populates="actor")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def role_names(self):
        return [ur.role.name for ur in self.roles]


class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(Enum(RoleType), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    permissions = Column(JSON, default=list)  # List of permission strings
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by_id = Column(String(36), nullable=True)  # Store as simple string, no FK to avoid ambiguity

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )

    # Relationships
    user = relationship("User", back_populates="roles", foreign_keys=[user_id])
    role = relationship("Role", back_populates="users")


# ============ Insurance & Plan Models ============

class InsuranceCompany(Base):
    __tablename__ = "insurance_companies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(20), nullable=True, unique=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    plans = relationship("Plan", back_populates="insurance_company")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    insurance_company_id = Column(String(36), ForeignKey("insurance_companies.id"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    
    # Auto-approval settings
    auto_approve_enabled = Column(Boolean, default=False)
    auto_approve_amount_cap = Column(Float, default=0.0)  # Max amount for auto-approval
    min_ocr_quality_score = Column(Float, default=0.8)    # Min OCR quality (0-1)
    min_confidence_score = Column(Float, default=0.85)    # Min extraction confidence
    max_duplicate_score = Column(Float, default=0.3)      # Max duplicate similarity allowed
    max_fraud_risk_score = Column(Float, default=0.2)     # Max fraud risk allowed
    required_documents = Column(JSON, default=list)       # Required doc types

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    insurance_company = relationship("InsuranceCompany", back_populates="plans")
    policies = relationship("MemberPolicy", back_populates="plan")
    claims = relationship("Claim", back_populates="plan")
    validation_rules = relationship("ValidationRule", back_populates="plan")


class MemberPolicy(Base):
    __tablename__ = "member_policies"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=False)
    member_id = Column(String(100), nullable=False)  # Insurance member ID
    group_number = Column(String(100), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(PolicyStatus), default=PolicyStatus.ACTIVE)
    coverage_details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('ix_member_policy_member_id', 'member_id'),
        UniqueConstraint('user_id', 'plan_id', 'member_id', name='uq_user_plan_member'),
    )

    # Relationships
    user = relationship("User", back_populates="policies")
    plan = relationship("Plan", back_populates="policies")


# ============ Claim Models ============

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=True)
    assigned_agent_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    status = Column(Enum(ClaimStatus), default=ClaimStatus.DRAFT, index=True)
    category = Column(Enum(ClaimCategory), default=ClaimCategory.OTHER)
    
    # Financial
    total_amount = Column(Float, default=0.0)
    approved_amount = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    
    # Details
    service_date = Column(DateTime, nullable=True)
    provider_name = Column(String(255), nullable=True)
    provider_npi = Column(String(20), nullable=True)  # National Provider Identifier
    diagnosis_codes = Column(JSON, default=list)       # ICD codes
    procedure_codes = Column(JSON, default=list)       # CPT codes
    description = Column(Text, nullable=True)
    
    # Processing metadata
    ocr_quality_score = Column(Float, nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    duplicate_score = Column(Float, default=0.0)
    fraud_risk_score = Column(Float, default=0.0)
    auto_approval_eligible = Column(Boolean, default=False)
    auto_approval_reasons = Column(JSON, default=list)
    
    # User-provided metadata
    user_notes = Column(Text, nullable=True)  # Optional notes from claimant
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True, index=True)  # Soft delete

    __table_args__ = (
        Index('ix_claim_user_status', 'user_id', 'status'),
        Index('ix_claim_agent_status', 'assigned_agent_id', 'status'),
    )

    # Relationships
    user = relationship("User", back_populates="claims", foreign_keys=[user_id])
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id])
    plan = relationship("Plan", back_populates="claims")
    documents = relationship("ClaimDocument", back_populates="claim", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="claim", cascade="all, delete-orphan")
    validation_results = relationship("ValidationResult", back_populates="claim", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="claim", cascade="all, delete-orphan")
    duplicate_matches = relationship("DuplicateMatch", back_populates="claim", 
                                     foreign_keys="DuplicateMatch.claim_id", cascade="all, delete-orphan")


class ClaimDocument(Base):
    __tablename__ = "claim_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash
    file_type = Column(String(50), nullable=True)  # MIME type
    file_size = Column(Integer, nullable=True)     # Size in bytes
    page_count = Column(Integer, default=1)
    ocr_quality_score = Column(Float, nullable=True)
    ocr_text = Column(Text, nullable=True)
    ocr_result_json = Column(JSON, nullable=True)
    document_type = Column(String(50), nullable=True)  # bill, eob, rx, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    claim = relationship("Claim", back_populates="documents")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    value = Column(Text, nullable=True)
    original_value = Column(Text, nullable=True)  # Original OCR value before correction
    confidence = Column(Float, default=0.0)
    source = Column(Enum(FieldSource), default=FieldSource.OCR)
    bounding_box = Column(JSON, nullable=True)  # Location in document
    page_number = Column(Integer, default=1)
    corrected_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    corrected_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_extracted_field_claim_name', 'claim_id', 'field_name'),
    )

    # Relationships
    claim = relationship("Claim", back_populates="extracted_fields")


# ============ Validation Models ============

class ValidationRule(Base):
    __tablename__ = "validation_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=True)  # Null = global rule
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    rule_type = Column(String(50), nullable=False)  # eligibility, amount, date, document, etc.
    condition_json = Column(JSON, nullable=False)   # Rule conditions
    error_message = Column(String(500), nullable=True)
    severity = Column(String(20), default="error")  # error, warning, info
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)  # Execution order
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    plan = relationship("Plan", back_populates="validation_rules")


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(String(36), ForeignKey("validation_rules.id"), nullable=True)
    rule_name = Column(String(100), nullable=False)
    passed = Column(Boolean, nullable=False)
    severity = Column(String(20), default="error")
    message = Column(Text, nullable=True)
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_validation_result_claim', 'claim_id'),
    )

    # Relationships
    claim = relationship("Claim", back_populates="validation_results")


# ============ Decision & Audit Models ============

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    decided_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Null for auto decisions
    decision = Column(Enum(DecisionType), nullable=False)
    reason_code = Column(String(50), nullable=True)
    reason_description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    approved_amount = Column(Float, nullable=True)
    is_auto_decision = Column(Boolean, default=False)
    auto_decision_reasons = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    claim = relationship("Claim", back_populates="decisions")
    decided_by = relationship("User", back_populates="decisions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False)  # claim, user, plan, etc.
    entity_id = Column(String(36), nullable=False)
    action = Column(String(50), nullable=False)       # create, update, delete, status_change, etc.
    actor_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    before_json = Column(JSON, nullable=True)
    after_json = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('ix_audit_log_entity', 'entity_type', 'entity_id'),
    )

    # Relationships
    actor = relationship("User", back_populates="audit_logs")


class DuplicateMatch(Base):
    __tablename__ = "duplicate_matches"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id", ondelete="CASCADE"), nullable=False)
    matched_claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    match_reasons_json = Column(JSON, nullable=True)  # Which fields matched
    is_confirmed_duplicate = Column(Boolean, default=False)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('claim_id', 'matched_claim_id', name='uq_duplicate_match'),
        Index('ix_duplicate_match_claim', 'claim_id'),
    )

    # Relationships
    claim = relationship("Claim", back_populates="duplicate_matches", foreign_keys=[claim_id])
    matched_claim = relationship("Claim", foreign_keys=[matched_claim_id])

