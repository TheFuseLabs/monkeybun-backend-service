from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BusinessCreateRequest(BaseModel):
    shop_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    instagram_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    facebook_handle: Optional[str] = None
    category: Optional[str] = None
    average_price_range: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    image_urls: Optional[list[str]] = None


class BusinessUpdateRequest(BaseModel):
    shop_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    instagram_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    facebook_handle: Optional[str] = None
    category: Optional[str] = None
    average_price_range: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    image_urls: Optional[list[str]] = None


class BusinessImageResponse(BaseModel):
    id: UUID
    business_id: UUID
    image_url: str
    caption: Optional[str] = None
    sort_order: Optional[int] = None


class BusinessImageUpdateRequest(BaseModel):
    caption: Optional[str] = None
    sort_order: Optional[int] = None


class BusinessResponse(BaseModel):
    id: UUID
    owner_user_id: UUID
    shop_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    instagram_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    twitter_handle: Optional[str] = None
    facebook_handle: Optional[str] = None
    category: Optional[str] = None
    average_price_range: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime
    images: Optional[list[BusinessImageResponse]] = None


class BusinessSearchFilters(BaseModel):
    category: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class BusinessSearchResponse(BaseModel):
    id: UUID
    shop_name: str
    category: Optional[str] = None
    logo_url: Optional[str] = None


class BusinessListResponse(BaseModel):
    businesses: list[BusinessSearchResponse]
    total: int
    limit: int
    offset: int

