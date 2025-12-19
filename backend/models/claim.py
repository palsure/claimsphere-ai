from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ClaimType(str, Enum):
    """Types of claims"""
    MEDICAL = "medical"
    INSURANCE = "insurance"
    TRAVEL = "travel"
    PROPERTY = "property"
    BUSINESS = "business"
    OTHER = "other"


class ClaimStatus(str, Enum):
    """Claim processing status"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_INFO = "requires_info"
    PROCESSED = "processed"


class ClaimItem(BaseModel):
    """Individual line item from a claim document"""
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: float
    category: Optional[str] = None


class Claim(BaseModel):
    """Claim record model"""
    id: Optional[str] = None
    claim_number: Optional[str] = None
    claimant_name: str
    claim_type: ClaimType
    date_of_incident: datetime
    date_submitted: datetime = Field(default_factory=datetime.now)
    total_amount: float
    approved_amount: Optional[float] = None
    currency: str = "USD"
    status: ClaimStatus = ClaimStatus.PENDING
    policy_number: Optional[str] = None
    items: List[ClaimItem] = []
    supporting_documents: List[str] = []  # URLs or paths to documents
    description: Optional[str] = None
    rejection_reason: Optional[str] = None
    reviewer_notes: Optional[str] = None
    language: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_duplicate: bool = False
    validation_errors: List[str] = []


class ClaimQuery(BaseModel):
    """Natural language query model for claims"""
    query: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    claim_type: Optional[ClaimType] = None
    status: Optional[ClaimStatus] = None


class ClaimAnalytics(BaseModel):
    """Analytics summary model for claims"""
    total_claims: int
    total_amount: float
    approved_amount: float
    pending_amount: float
    status_breakdown: dict
    type_breakdown: dict
    monthly_trends: List[dict]
    average_processing_time: float  # in days
    approval_rate: float
    top_claimants: List[dict]

