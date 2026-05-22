from typing import Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.user import User
from apps.api.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return await super().get_by_id(user_id)

    async def update_resume(
        self,
        user: User,
        *,
        resume_s3_key: Optional[str] = None,
        resume_text: Optional[str] = None,
        resume_embedding: Optional[list[float]] = None,
    ) -> User:
        if resume_s3_key is not None:
            user.resume_s3_key = resume_s3_key
        if resume_text is not None:
            user.resume_text = resume_text
        if resume_embedding is not None:
            user.resume_embedding = resume_embedding
        await self.session.flush()
        await self.session.refresh(user)
        return user
