from datetime import datetime, timezone
from typing import List, Optional, Sequence
import uuid

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.job_posting import ExperienceLevel, JobPosting, JobSource, WorkMode
from apps.api.repositories.base import BaseRepository


class JobRepository(BaseRepository[JobPosting]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, JobPosting)

    async def list_active(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        work_modes: Optional[Sequence[WorkMode]] = None,
        experience_levels: Optional[Sequence[ExperienceLevel]] = None,
    ) -> List[JobPosting]:
        query = select(JobPosting).where(JobPosting.is_active.is_(True))
        if work_modes:
            query = query.where(JobPosting.work_mode.in_(work_modes))
        if experience_levels:
            query = query.where(JobPosting.experience_level.in_(experience_levels))
        query = query.order_by(JobPosting.posted_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_active(self) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(JobPosting).where(
                JobPosting.is_active.is_(True)
            )
        )
        return int(result.scalar_one())

    async def get_by_source_external(
        self, source: JobSource, external_id: str
    ) -> Optional[JobPosting]:
        result = await self.session.execute(
            select(JobPosting).where(
                and_(
                    JobPosting.source == source,
                    JobPosting.external_id == external_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def upsert(self, job: JobPosting) -> tuple[JobPosting, bool]:
        existing = await self.get_by_source_external(job.source, job.external_id)
        if existing:
            existing.title = job.title
            existing.company = job.company
            existing.location = job.location
            existing.work_mode = job.work_mode
            existing.experience_level = job.experience_level
            existing.description = job.description
            existing.url = job.url
            existing.salary_min = job.salary_min
            existing.salary_max = job.salary_max
            existing.posted_at = job.posted_at
            existing.parsed_jd = job.parsed_jd
            existing.is_active = True
            existing.scraped_at = datetime.now(timezone.utc)
            await self.session.flush()
            await self.session.refresh(existing)
            return existing, False
        return await self.create(job), True

    async def update_embedding(
        self, job: JobPosting, embedding: list[float]
    ) -> JobPosting:
        job.embedding = embedding
        await self.session.flush()
        await self.session.refresh(job)
        return job

    async def list_without_embedding(self, limit: int = 100) -> List[JobPosting]:
        result = await self.session.execute(
            select(JobPosting)
            .where(
                and_(
                    JobPosting.is_active.is_(True),
                    JobPosting.embedding.is_(None),
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def find_matches_for_user(
        self,
        user_embedding: list[float],
        *,
        min_score: float = 0.7,
        limit: int = 50,
        work_modes: Optional[Sequence[WorkMode]] = None,
        experience_levels: Optional[Sequence[ExperienceLevel]] = None,
    ) -> List[tuple[JobPosting, float]]:
        distance = JobPosting.embedding.cosine_distance(user_embedding)
        score = (1 - distance).label("match_score")
        query = (
            select(JobPosting, score)
            .where(
                and_(
                    JobPosting.is_active.is_(True),
                    JobPosting.embedding.is_not(None),
                )
            )
            .where((1 - distance) >= min_score)
        )
        if work_modes:
            query = query.where(JobPosting.work_mode.in_(work_modes))
        if experience_levels:
            query = query.where(JobPosting.experience_level.in_(experience_levels))
        query = query.order_by(score.desc()).limit(limit)
        result = await self.session.execute(query)
        return [(row[0], float(row[1])) for row in result.all()]
