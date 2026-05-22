from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from apps.api.models.job_posting import ExperienceLevel, JobSource, WorkMode


class JobPostingBase(BaseModel):
    external_id: str
    source: JobSource
    title: str
    company: str
    location: str = ""
    work_mode: WorkMode
    experience_level: ExperienceLevel
    description: str
    url: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    posted_at: datetime


class JobPostingCreate(JobPostingBase):
    parsed_jd: Optional[dict[str, Any]] = None


class JobPostingResponse(JobPostingBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool = True
    match_score: Optional[float] = None


class JobMatchQuery(BaseModel):
    min_score: float = Field(default=0.7, ge=0.0, le=1.0)
