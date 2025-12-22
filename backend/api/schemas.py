"""Pydantic schemas for API requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from backend.database.models import (
    ClaimStatus, ClaimCategory, DecisionType, 
    PolicyStatus, FieldSource, RoleType
)


# ============ Insurance Company Schemas ============

class InsuranceCompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None


class InsuranceCompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    is_active: Optional[bool] = None


class InsuranceCompanyResponse(BaseModel):
    id: str
    name: str
    code: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Plan Schemas ============

class PlanCreate(BaseModel):
    insurance_company_id: str
    name: str = Field(..., min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    auto_approve_enabled: bool = False
    auto_approve_amount_cap: float = 0.0
    min_ocr_quality_score: float = Field(0.8, ge=0, le=1)
    min_confidence_score: float = Field(0.85, ge=0, le=1)
    max_duplicate_score: float = Field(0.3, ge=0, le=1)
    max_fraud_risk_score: float = Field(0.2, ge=0, le=1)
    required_documents: List[str] = []


class PlanUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    auto_approve_enabled: Optional[bool] = None
    auto_approve_amount_cap: Optional[float] = None
    min_ocr_quality_score: Optional[float] = Field(None, ge=0, le=1)
    min_confidence_score: Optional[float] = Field(None, ge=0, le=1)
    max_duplicate_score: Optional[float] = Field(None, ge=0, le=1)
    max_fraud_risk_score: Optional[float] = Field(None, ge=0, le=1)
    required_documents: Optional[List[str]] = None
    is_active: Optional[bool] = None


class PlanResponse(BaseModel):
    id: str
    insurance_company_id: str
    name: str
    code: Optional[str]
    description: Optional[str]
    auto_approve_enabled: bool
    auto_approve_amount_cap: float
    min_ocr_quality_score: float
    min_confidence_score: float
    max_duplicate_score: float
    max_fraud_risk_score: float
    required_documents: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Member Policy Schemas ============

class MemberPolicyCreate(BaseModel):
    user_id: str
    plan_id: str
    member_id: str = Field(..., min_length=1, max_length=100)
    group_number: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    coverage_details: Dict[str, Any] = {}


class MemberPolicyResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    member_id: str
    group_number: Optional[str]
    start_date: datetime
    end_date: Optional[datetime]
    status: PolicyStatus
    coverage_details: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Claim Schemas ============

class ClaimCreate(BaseModel):
    plan_id: Optional[str] = None
    category: ClaimCategory = ClaimCategory.OTHER
    total_amount: float = Field(..., ge=0)
    currency: str = Field("USD", max_length=3)
    service_date: Optional[datetime] = None
    provider_name: Optional[str] = None
    provider_npi: Optional[str] = None
    diagnosis_codes: List[str] = []
    procedure_codes: List[str] = []
    description: Optional[str] = None


class ClaimUpdate(BaseModel):
    category: Optional[ClaimCategory] = None
    total_amount: Optional[float] = Field(None, ge=0)
    service_date: Optional[datetime] = None
    provider_name: Optional[str] = None
    provider_npi: Optional[str] = None
    diagnosis_codes: Optional[List[str]] = None
    procedure_codes: Optional[List[str]] = None
    description: Optional[str] = None


class ClaimStatusUpdate(BaseModel):
    status: ClaimStatus
    notes: Optional[str] = None


class ExtractedFieldResponse(BaseModel):
    id: str
    field_name: str
    value: Optional[str]
    original_value: Optional[str]
    confidence: float
    source: FieldSource
    page_number: int

    class Config:
        from_attributes = True


class ExtractedFieldCorrection(BaseModel):
    field_name: str
    value: str


class ClaimDocumentResponse(BaseModel):
    id: str
    file_name: str
    file_url: str
    file_type: Optional[str]
    page_count: int
    ocr_quality_score: Optional[float]
    document_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ValidationResultResponse(BaseModel):
    id: str
    rule_name: str
    passed: bool
    severity: str
    message: Optional[str]
    details_json: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class DuplicateMatchResponse(BaseModel):
    id: str
    matched_claim_id: str
    matched_claim_number: Optional[str] = None
    similarity_score: float
    match_reasons_json: Optional[Dict[str, Any]]
    is_confirmed_duplicate: bool

    class Config:
        from_attributes = True


class DecisionResponse(BaseModel):
    id: str
    decision: DecisionType
    reason_code: Optional[str]
    reason_description: Optional[str]
    notes: Optional[str]
    approved_amount: Optional[float]
    is_auto_decision: bool
    decided_by_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ClaimResponse(BaseModel):
    id: str
    claim_number: str
    user_id: str
    claimant_name: Optional[str] = None
    plan_id: Optional[str]
    assigned_agent_id: Optional[str]
    status: ClaimStatus
    category: ClaimCategory
    total_amount: float
    approved_amount: Optional[float]
    currency: str
    service_date: Optional[datetime]
    provider_name: Optional[str]
    description: Optional[str]
    ocr_quality_score: Optional[float]
    extraction_confidence: Optional[float]
    duplicate_score: float
    fraud_risk_score: float
    is_duplicate: bool = False
    auto_approval_eligible: bool
    created_at: datetime
    submitted_at: Optional[datetime]
    
    # Nested data
    documents: List[ClaimDocumentResponse] = []
    extracted_fields: List[ExtractedFieldResponse] = []
    validation_results: List[ValidationResultResponse] = []
    decisions: List[DecisionResponse] = []
    duplicate_matches: List[DuplicateMatchResponse] = []

    class Config:
        from_attributes = True


class ClaimListResponse(BaseModel):
    id: str
    claim_number: str
    user_id: str
    claimant_name: Optional[str] = None  # Extracted from document
    status: ClaimStatus
    category: ClaimCategory
    total_amount: float
    approved_amount: Optional[float]
    currency: str
    service_date: Optional[datetime]
    provider_name: Optional[str]
    created_at: datetime
    submitted_at: Optional[datetime]
    is_duplicate: bool = False
    duplicate_score: float = 0.0

    class Config:
        from_attributes = True


# ============ Decision Schemas ============

class DecisionCreate(BaseModel):
    decision: DecisionType
    reason_code: Optional[str] = None
    reason_description: Optional[str] = None
    notes: Optional[str] = None
    approved_amount: Optional[float] = None


# ============ Validation Rule Schemas ============

class ValidationRuleCreate(BaseModel):
    plan_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    rule_type: str = Field(..., min_length=1, max_length=50)
    condition_json: Dict[str, Any]
    error_message: Optional[str] = None
    severity: str = "error"
    order: int = 0


class ValidationRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    rule_type: Optional[str] = Field(None, max_length=50)
    condition_json: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    order: Optional[int] = None


class ValidationRuleResponse(BaseModel):
    id: str
    plan_id: Optional[str]
    name: str
    description: Optional[str]
    rule_type: str
    condition_json: Dict[str, Any]
    error_message: Optional[str]
    severity: str
    is_active: bool
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Query Schemas ============

class NaturalLanguageQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    claim_type: Optional[ClaimCategory] = None
    status: Optional[ClaimStatus] = None


class QueryResponse(BaseModel):
    query: str
    answer: str
    claims_analyzed: int
    cited_claims: List[str] = []  # Claim IDs used in response
    fields_used: List[str] = []   # Field names used


# ============ Analytics Schemas ============

class ClaimAnalytics(BaseModel):
    total_claims: int
    total_amount: float
    approved_amount: float
    pending_amount: float
    denied_amount: float
    status_breakdown: Dict[str, int]
    category_breakdown: Dict[str, int]
    monthly_trends: List[Dict[str, Any]]
    average_processing_time_hours: float
    auto_approval_rate: float
    approval_rate: float


# ============ Audit Log Schemas ============

class AuditLogResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    action: str
    actor_user_id: Optional[str]
    actor_name: Optional[str] = None
    before_json: Optional[Dict[str, Any]]
    after_json: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Pagination ============

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int

