from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FavoriteCreateRequest(BaseModel):
    market_id: UUID


class FavoriteResponse(BaseModel):
    id: UUID
    market_id: UUID
    user_id: UUID
    created_at: datetime


class FavoriteListFilters(BaseModel):
    market_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class FavoriteListResponse(BaseModel):
    favorites: list[FavoriteResponse]
    total: int
    limit: int
    offset: int
