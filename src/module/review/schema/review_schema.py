from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    target_type: str = Field(..., pattern="^(market|business)$")
    target_id: UUID
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    body: Optional[str] = None
    is_published: bool = True


class ReviewUpdateRequest(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    body: Optional[str] = None
    is_published: Optional[bool] = None


class ReviewResponse(BaseModel):
    id: UUID
    author_user_id: UUID
    target_type: str
    target_id: UUID
    rating: Optional[int] = None
    title: Optional[str] = None
    body: Optional[str] = None
    is_published: bool
    created_at: datetime


class ReviewListFilters(BaseModel):
    target_type: Optional[str] = Field(None, pattern="^(market|business)$")
    target_id: Optional[UUID] = None
    author_user_id: Optional[UUID] = None
    is_published: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ReviewListResponse(BaseModel):
    reviews: list[ReviewResponse]
    total: int
    limit: int
    offset: int


class ReviewStatsResponse(BaseModel):
    target_type: str
    target_id: UUID
    total_reviews: int
    average_rating: Optional[float] = None

