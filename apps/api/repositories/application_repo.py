from typing import List, Optional
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.models.application import Application, ApplicationStatus
from apps.api.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Application)

    async def list_for_user(self, user_id: uuid.UUID) -> List[Application]:
        result = await self.session.execute(
            select(Application)
            .where(Application.user_id == user_id)
            .options(selectinload(Application.job))
            .order_by(Application.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_for_user(
        self, application_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Application]:
        result = await self.session.execute(
            select(Application)
            .where(
                Application.id == application_id,
                Application.user_id == user_id,
            )
            .options(selectinload(Application.job))
        )
        return result.scalar_one_or_none()

    async def get_by_user_job(
        self, user_id: uuid.UUID, job_id: uuid.UUID
    ) -> Optional[Application]:
        result = await self.session.execute(
            select(Application).where(
                Application.user_id == user_id,
                Application.job_id == job_id,
            )
        )
        return result.scalar_one_or_none()

    async def count_by_status(
        self, user_id: uuid.UUID, statuses: List[ApplicationStatus]
    ) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Application)
            .where(
                Application.user_id == user_id,
                Application.status.in_(statuses),
            )
        )
        return int(result.scalar_one())

    async def update_status(
        self,
        application: Application,
        status: ApplicationStatus,
        *,
        cover_letter: Optional[str] = None,
        tailored_resume_key: Optional[str] = None,
    ) -> Application:
        application.status = status
        if cover_letter is not None:
            application.cover_letter = cover_letter
        if tailored_resume_key is not None:
            application.tailored_resume_key = tailored_resume_key
        await self.session.flush()
        await self.session.refresh(application)
        return application
