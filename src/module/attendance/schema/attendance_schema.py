from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AttendanceCreateRequest(BaseModel):
    market_id: UUID
    status: str = Field(default="attending")
    calendar_event_id: Optional[str] = None


class AttendanceUpdateRequest(BaseModel):
    status: Optional[str] = None
    calendar_event_id: Optional[str] = None


class AttendanceResponse(BaseModel):
    id: UUID
    market_id: UUID
    user_id: UUID
    status: str
    calendar_event_id: Optional[str] = None
    created_at: datetime


class AttendanceListFilters(BaseModel):
    market_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    status: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class AttendanceListResponse(BaseModel):
    attendances: list[AttendanceResponse]
    total: int
    limit: int
    offset: int

