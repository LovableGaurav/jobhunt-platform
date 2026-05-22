from typing import List
import uuid

from fastapi import APIRouter, HTTPException, Query, status

from apps.api.core.dependencies import CurrentUser, DbSession
from apps.api.repositories.job_repo import JobRepository
from apps.api.schemas.job import JobPostingResponse
from apps.api.services.job_filter import JobFilterService
from apps.api.services.matcher import MatcherService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=List[JobPostingResponse])
async def list_jobs(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> List[JobPostingResponse]:
    del current_user
    job_filter = JobFilterService()
    repo = JobRepository(db)
    jobs = await repo.list_active(
        skip=skip,
        limit=limit,
        work_modes=job_filter.allowed_work_modes,
        experience_levels=job_filter.allowed_experience,
    )
    return [JobPostingResponse.model_validate(j) for j in jobs]


@router.get("/matches", response_model=List[JobPostingResponse])
async def list_matches(
    db: DbSession,
    current_user: CurrentUser,
    min_score: float = Query(0.7, ge=0.0, le=1.0),
) -> List[JobPostingResponse]:
    matcher = MatcherService(db)
    return await matcher.get_matches(current_user, min_score=min_score)


@router.get("/{job_id}", response_model=JobPostingResponse)
async def get_job(
    job_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> JobPostingResponse:
    del current_user
    job = await JobRepository(db).get_by_id(job_id)
    if not job or not job.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobPostingResponse.model_validate(job)
