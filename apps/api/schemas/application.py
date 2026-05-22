from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from apps.api.models.application import ApplicationStatus
from apps.api.schemas.job import JobPostingResponse


class ApplicationCreate(BaseModel):
    job_id: UUID


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    user_id: UUID
    status: ApplicationStatus
    tailored_resume_key: Optional[str] = None
    cover_letter: Optional[str] = None
    match_score: float
    applied_at: Optional[datetime] = None
    created_at: datetime
    job: Optional[JobPostingResponse] = None


class DashboardStatsResponse(BaseModel):
    total_jobs: int
    matched_jobs: int
    applications_submitted: int
    interviews: int
    match_rate: float
