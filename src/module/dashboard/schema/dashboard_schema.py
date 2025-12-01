from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ApplicationStats(BaseModel):
    total: int
    applied: int
    accepted: int
    declined: int
    confirmed: int


class DashboardStatsResponse(BaseModel):
    businesses_count: int
    markets_count: int
    applications: ApplicationStats
    reviews_written_count: int
