from fastapi import APIRouter

from apps.api.core.config import get_settings
from apps.api.core.dependencies import CurrentUser, DbSession
from apps.api.models.application import ApplicationStatus
from apps.api.repositories.application_repo import ApplicationRepository
from apps.api.repositories.job_repo import JobRepository
from apps.api.schemas.application import DashboardStatsResponse
from apps.api.services.matcher import MatcherService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
settings = get_settings()


@router.get("/stats", response_model=DashboardStatsResponse)
async def dashboard_stats(
    db: DbSession,
    current_user: CurrentUser,
) -> DashboardStatsResponse:
    job_repo = JobRepository(db)
    app_repo = ApplicationRepository(db)
    matcher = MatcherService(db)

    total_jobs = await job_repo.count_active()
    matches = await matcher.get_matches(
        current_user,
        min_score=settings.match_score_threshold,
        limit=500,
    )
    submitted = await app_repo.count_by_status(
        current_user.id,
        [ApplicationStatus.submitted, ApplicationStatus.viewed],
    )
    interviews = await app_repo.count_by_status(
        current_user.id,
        [ApplicationStatus.interview, ApplicationStatus.offer],
    )
    match_rate = len(matches) / total_jobs if total_jobs > 0 else 0.0

    return DashboardStatsResponse(
        total_jobs=total_jobs,
        matched_jobs=len(matches),
        applications_submitted=submitted,
        interviews=interviews,
        match_rate=min(match_rate, 1.0),
    )
