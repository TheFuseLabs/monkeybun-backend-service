from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


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


class Business(SQLModel, table=True):
    __tablename__ = "businesses"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    owner_user_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True)))
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
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(server_default=func.now()),
    )


class BusinessImage(SQLModel, table=True):
    __tablename__ = "business_images"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    business_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
        )
    )
    image_url: str
    caption: Optional[str] = None
    sort_order: Optional[int] = None


class Market(SQLModel, table=True):
    __tablename__ = "markets"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    organizer_user_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True)))
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
    is_published: bool = Field(default=True)
    email_package_url: Optional[str] = None
    payment_instructions: Optional[str] = None
    application_form: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
    )
    logo_url: Optional[str] = None
    is_free: bool = Field(default=False)
    cost_amount: Optional[float] = None
    cost_currency: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(server_default=func.now()),
    )


class MarketImage(SQLModel, table=True):
    __tablename__ = "market_images"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    market_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE")
        )
    )
    image_url: str
    caption: Optional[str] = None
    sort_order: Optional[int] = None


class Application(SQLModel, table=True):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "market_id", "business_id", name="applications_market_id_business_id_key"
        ),
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    market_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE")
        )
    )
    business_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), ForeignKey("businesses.id", ondelete="CASCADE")
        )
    )
    status: ApplicationStatus = Field(
        default=ApplicationStatus.applied,
        sa_column=Column(SQLEnum(ApplicationStatus, native_enum=False, length=50)),
    )
    applied_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(server_default=func.now()),
    )
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    declined_at: Optional[datetime] = None
    notes_for_org: Optional[str] = None
    rejection_reason: Optional[str] = None
    payment_method: Optional[PaymentMethod] = Field(
        default=None,
        sa_column=Column(SQLEnum(PaymentMethod, native_enum=False, length=50)),
    )
    payment_status: Optional[PaymentStatus] = Field(
        default=None,
        sa_column=Column(SQLEnum(PaymentStatus, native_enum=False, length=50)),
    )
    answers: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(server_default=func.now()),
    )


class MarketAttendance(SQLModel, table=True):
    __tablename__ = "market_attendance"
    __table_args__ = (
        UniqueConstraint(
            "market_id", "user_id", name="market_attendance_market_id_user_id_key"
        ),
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    market_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE")
        )
    )
    user_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True)))
    status: str = Field(default="attending")
    calendar_event_id: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(server_default=func.now()),
    )


class MarketFavorite(SQLModel, table=True):
    __tablename__ = "market_favorites"
    __table_args__ = (
        UniqueConstraint(
            "market_id", "user_id", name="market_favorites_market_id_user_id_key"
        ),
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    market_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE")
        )
    )
    user_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True)))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(server_default=func.now()),
    )


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        Index("reviews_target_idx", "target_type", "target_id"),
        CheckConstraint(
            "rating IS NULL OR (rating >= 1 AND rating <= 5)",
            name="reviews_rating_check",
        ),
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    author_user_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True)))
    target_type: str
    target_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True)))
    rating: Optional[int] = None
    title: Optional[str] = None
    body: Optional[str] = None
    is_published: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(server_default=func.now()),
    )


class ReviewImage(SQLModel, table=True):
    __tablename__ = "review_images"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    review_id: UUID = Field(
        sa_column=Column(
            PGUUID(as_uuid=True), ForeignKey("reviews.id", ondelete="CASCADE")
        )
    )
    image_url: str
    caption: Optional[str] = None


class PendingImage(SQLModel, table=True):
    __tablename__ = "pending_images"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            PGUUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        ),
    )
    user_id: UUID = Field(sa_column=Column(PGUUID(as_uuid=True)))
    image_url: str
    s3_key: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(server_default=func.now()),
    )
