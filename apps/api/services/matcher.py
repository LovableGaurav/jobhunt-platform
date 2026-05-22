from typing import List, Optional, Tuple
import uuid

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.config import get_settings
from apps.api.models.job_posting import ExperienceLevel, JobPosting, WorkMode
from apps.api.models.user import User
from apps.api.repositories.job_repo import JobRepository
from apps.api.repositories.user_repo import UserRepository
from apps.api.schemas.job import JobPostingResponse
from apps.api.services.job_filter import JobFilterService

settings = get_settings()


class MatcherService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.job_repo = JobRepository(session)
        self.user_repo = UserRepository(session)
        self.filter = JobFilterService()
        self._openai: Optional[AsyncOpenAI] = None

    @property
    def openai(self) -> AsyncOpenAI:
        if self._openai is None:
            self._openai = AsyncOpenAI(api_key=settings.openai_api_key or None)
        return self._openai

    async def embed_text(self, text: str) -> list[float]:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for embeddings")
        response = await self.openai.embeddings.create(
            model=settings.openai_embedding_model,
            input=text[:8000],
        )
        return response.data[0].embedding

    async def embed_user_resume(self, user: User) -> User:
        if not user.resume_text:
            return user
        embedding = await self.embed_text(user.resume_text)
        return await self.user_repo.update_resume(user, resume_embedding=embedding)

    async def embed_job(self, job: JobPosting) -> JobPosting:
        text = f"{job.title}\n{job.company}\n{job.description}"
        embedding = await self.embed_text(text)
        return await self.job_repo.update_embedding(job, embedding)

    async def get_matches(
        self,
        user: User,
        *,
        min_score: Optional[float] = None,
        limit: int = 50,
    ) -> List[JobPostingResponse]:
        threshold = min_score if min_score is not None else settings.match_score_threshold
        if user.resume_embedding is None and user.resume_text:
            user = await self.embed_user_resume(user)
        if user.resume_embedding is None:
            return []

        rows = await self.job_repo.find_matches_for_user(
            list(user.resume_embedding),
            min_score=threshold,
            limit=limit,
            work_modes=self.filter.allowed_work_modes,
            experience_levels=self.filter.allowed_experience,
        )
        results: List[JobPostingResponse] = []
        for job, score in rows:
            resp = JobPostingResponse.model_validate(job)
            resp.match_score = score
            results.append(resp)
        return results

    async def score_pair(self, user: User, job: JobPosting) -> float:
        if user.resume_embedding is None or job.embedding is None:
            return 0.0
        rows = await self.job_repo.find_matches_for_user(
            list(user.resume_embedding),
            min_score=0.0,
            limit=1,
        )
        for matched_job, score in rows:
            if matched_job.id == job.id:
                return score
        return 0.0
