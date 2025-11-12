from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class ResumeStatus(str, Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ResumeTemplateName(str, Enum):
    JAKE = "JAKE"
    RENDERCV = "RENDERCV"


class Resume(SQLModel, table=True):
    __tablename__ = "resumes"

    id: UUID = Field(primary_key=True, index=True)
    user_id: UUID = Field(nullable=False, index=True)
    resume_title: str = Field(nullable=False)
    resume_description: Optional[str] = Field(default=None)
    job_description: Optional[str] = Field(default=None)
    additional_instructions: Optional[str] = Field(default=None)
    source_pdf_url: Optional[str] = Field(default=None)
    compiled_resume_pdf_url: Optional[str] = Field(default=None)
    tailored_resume_latex_url: Optional[str] = Field(default=None)
    resume_data_json: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSONB)
    )
    template_name: ResumeTemplateName = Field(nullable=False)
    status: ResumeStatus = Field(nullable=False, default=ResumeStatus.QUEUED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)


class TrialState(SQLModel, table=True):
    __tablename__ = "trial_state"

    user_id: UUID = Field(primary_key=True, nullable=False)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resumes_used: int = Field(default=0)
    resumes_limit: int = Field(default=5)
    last_refresh_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    next_refresh_at: datetime = Field(nullable=False)
    is_active: bool = Field(default=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
