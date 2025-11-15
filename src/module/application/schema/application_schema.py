from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    applied = "applied"
    accepted = "accepted"
    declined = "declined"
    confirmed = "confirmed"


class PaymentMethod(str, Enum):
    bank_transfer = "bank_transfer"
    credit_card = "credit_card"
    paypal = "paypal"
    check = "check"
    cash = "cash"
    other = "other"


class PaymentStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class ApplicationCreateRequest(BaseModel):
    market_id: UUID
    business_id: UUID
    answers: Optional[Dict[str, Any]] = None


class ApplicationUpdateRequest(BaseModel):
    status: Optional[ApplicationStatus] = None
    notes_for_org: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = None
    answers: Optional[Dict[str, Any]] = None


class ApplicationPaymentUpdateRequest(BaseModel):
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = None


class ApplicationConfirmRequest(BaseModel):
    pass


class ApplicationAcceptRequest(BaseModel):
    pass


class ApplicationRejectRequest(BaseModel):
    rejection_reason: str


class ApplicationResponse(BaseModel):
    id: UUID
    market_id: UUID
    business_id: UUID
    status: ApplicationStatus
    applied_at: datetime
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    declined_at: Optional[datetime] = None
    notes_for_org: Optional[str] = None
    rejection_reason: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = None
    answers: Optional[Dict[str, Any]] = None
    created_at: datetime


class ApplicationSearchFilters(BaseModel):
    market_id: Optional[UUID] = None
    business_id: Optional[UUID] = None
    status: Optional[ApplicationStatus] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ApplicationSearchResponse(BaseModel):
    id: UUID
    market_id: UUID
    business_id: UUID
    status: ApplicationStatus
    applied_at: datetime
    rejection_reason: Optional[str] = None
    created_at: datetime


class ApplicationListResponse(BaseModel):
    applications: list[ApplicationSearchResponse]
    total: int
    limit: int
    offset: int

