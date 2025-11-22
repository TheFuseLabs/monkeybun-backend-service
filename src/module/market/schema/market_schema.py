from datetime import date, datetime
from typing import Any, Dict, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class MarketCreateRequest(BaseModel):
    market_name: str
    contact_first_name: str
    contact_last_name: str
    email: str
    phone: Optional[str] = None
    google_place_id: str
    location_text: str
    aesthetic: Optional[str] = None
    market_size: Literal["Less than 10", "10-99", "100-499", "500-999", "1000+"]
    target_vendors: Optional[str] = None
    optional_rules: Optional[str] = None
    contract_url: Optional[str] = None
    description: str
    start_date: date
    end_date: date
    application_deadline: datetime
    email_package_url: Optional[str] = None
    payment_instructions: Optional[str] = None
    application_form: Dict[str, Any]
    logo_url: Optional[str] = None
    image_urls: Optional[list[str]] = None
    is_free: bool
    cost_amount: Optional[float] = None
    cost_currency: Optional[Literal["CAD", "USD"]] = None

    @model_validator(mode="after")
    def validate_cost_fields(self):
        if not self.is_free:
            if self.cost_amount is None:
                raise ValueError("cost_amount is required when is_free is False")
            if self.cost_currency is None:
                raise ValueError("cost_currency is required when is_free is False")
            if not self.payment_instructions:
                raise ValueError(
                    "payment_instructions is required when is_free is False"
                )
        return self


class MarketUpdateRequest(BaseModel):
    market_name: Optional[str] = None
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    google_place_id: Optional[str] = None
    location_text: Optional[str] = None
    aesthetic: Optional[str] = None
    market_size: Optional[
        Literal["Less than 10", "10-99", "100-499", "500-999", "1000+"]
    ] = None
    target_vendors: Optional[str] = None
    optional_rules: Optional[str] = None
    contract_url: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    application_deadline: Optional[datetime] = None
    email_package_url: Optional[str] = None
    payment_instructions: Optional[str] = None
    application_form: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = None
    image_urls: Optional[list[str]] = None
    is_free: Optional[bool] = None
    cost_amount: Optional[float] = None
    cost_currency: Optional[Literal["CAD", "USD"]] = None

    @model_validator(mode="after")
    def validate_cost_fields(self):
        if self.is_free is False:
            if self.cost_amount is None:
                raise ValueError("cost_amount is required when is_free is False")
            if self.cost_currency is None:
                raise ValueError("cost_currency is required when is_free is False")
            if (
                self.payment_instructions is None
                or self.payment_instructions.strip() == ""
            ):
                raise ValueError(
                    "payment_instructions is required when is_free is False"
                )
        return self


class MarketImageResponse(BaseModel):
    id: UUID
    market_id: UUID
    image_url: str
    caption: Optional[str] = None
    sort_order: Optional[int] = None


class MarketImageCreateRequest(BaseModel):
    image_url: str
    caption: Optional[str] = None
    sort_order: Optional[int] = None


class MarketImageUpdateRequest(BaseModel):
    caption: Optional[str] = None
    sort_order: Optional[int] = None


class MarketResponse(BaseModel):
    id: UUID
    organizer_user_id: UUID
    market_name: str
    contact_first_name: Optional[str] = None
    contact_last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location_text: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    google_place_id: Optional[str] = None
    formatted_address: Optional[str] = None
    aesthetic: Optional[str] = None
    market_size: Optional[str] = None
    target_vendors: Optional[str] = None
    optional_rules: Optional[str] = None
    contract_url: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    application_deadline: Optional[datetime] = None
    email_package_url: Optional[str] = None
    payment_instructions: Optional[str] = None
    application_form: Optional[Dict[str, Any]] = None
    logo_url: Optional[str] = None
    is_free: bool
    cost_amount: Optional[float] = None
    cost_currency: Optional[str] = None
    created_at: datetime
    images: Optional[list[MarketImageResponse]] = None
    review_count: Optional[int] = None
    average_rating: Optional[float] = None
    attendance_count: Optional[int] = None


class MarketSearchFilters(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    is_published: Optional[bool] = None
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    end_date_from: Optional[date] = None
    end_date_to: Optional[date] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = Field(None, ge=0, le=1000)
    aesthetic: Optional[str] = None
    market_size: Optional[str] = None
    is_free: Optional[bool] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class MarketSearchResponse(BaseModel):
    id: UUID
    market_name: str
    location_text: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    formatted_address: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    logo_url: Optional[str] = None
    image_url: Optional[str] = None
    review_count: Optional[int] = None
    average_rating: Optional[float] = None
    aesthetic: Optional[str] = None
    market_size: Optional[str] = None
    is_free: Optional[bool] = None
    description: Optional[str] = None
    cost_amount: Optional[float] = None
    cost_currency: Optional[str] = None
    application_deadline: Optional[datetime] = None
    images: Optional[list[str]] = None
    attendance_count: Optional[int] = None


class MarketListResponse(BaseModel):
    markets: list[MarketSearchResponse]
    total: int
    limit: int
    offset: int
