from datetime import datetime, timezone
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.application import Application, ApplicationStatus
from apps.api.repositories.application_repo import ApplicationRepository
from apps.api.repositories.job_repo import JobRepository
from apps.api.repositories.user_repo import UserRepository
from apps.api.services.ai_tailor import AITailorService
from apps.api.services.matcher import MatcherService


class ApplicationBotService:
    """Queues and processes auto-apply workflow."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.app_repo = ApplicationRepository(session)
        self.job_repo = JobRepository(session)
        self.user_repo = UserRepository(session)
        self.matcher = MatcherService(session)
        self.tailor = AITailorService()

    async def create_application(
        self,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
    ) -> Application:
        existing = await self.app_repo.get_by_user_job(user_id, job_id)
        if existing:
            return existing

        user = await self.user_repo.get_by_id(user_id)
        job = await self.job_repo.get_by_id(job_id)
        if not user or not job:
            raise ValueError("User or job not found")

        match_score = await self.matcher.score_pair(user, job)
        if match_score == 0.0 and user.resume_embedding and job.embedding:
            match_score = 0.5

        application = Application(
            user_id=user_id,
            job_id=job_id,
            status=ApplicationStatus.queued,
            match_score=match_score,
        )
        application = await self.app_repo.create(application)

        application = await self.tailor.apply_to_application(user, job, application)
        application.status = ApplicationStatus.submitted
        application.applied_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(application)
        return application
