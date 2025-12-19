from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ExpenseCategory(str, Enum):
    """Expense categories"""
    MEALS = "meals"
    TRAVEL = "travel"
    OFFICE_SUPPLIES = "office_supplies"
    UTILITIES = "utilities"
    SOFTWARE = "software"
    MARKETING = "marketing"
    PROFESSIONAL_SERVICES = "professional_services"
    RENT = "rent"
    INSURANCE = "insurance"
    OTHER = "other"


class ExpenseStatus(str, Enum):
    """Expense processing status"""
    PENDING = "pending"
    PROCESSED = "processed"
    VERIFIED = "verified"
    REJECTED = "rejected"


class ExpenseItem(BaseModel):
    """Individual line item from a receipt"""
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: float


class Expense(BaseModel):
    """Expense record model"""
    id: Optional[str] = None
    merchant_name: str
    date: datetime
    total_amount: float
    tax_amount: Optional[float] = None
    currency: str = "USD"
    category: Optional[ExpenseCategory] = None
    items: List[ExpenseItem] = []
    receipt_image_url: Optional[str] = None
    status: ExpenseStatus = ExpenseStatus.PENDING
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    is_duplicate: bool = False
    language: Optional[str] = None


class ExpenseQuery(BaseModel):
    """Natural language query model"""
    query: str
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    category: Optional[ExpenseCategory] = None


class ExpenseAnalytics(BaseModel):
    """Analytics summary model"""
    total_expenses: float
    expense_count: int
    category_breakdown: dict
    monthly_trends: List[dict]
    top_merchants: List[dict]
    tax_deductible_total: float

