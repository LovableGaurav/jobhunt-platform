"""Async DB helpers for Celery tasks."""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.database import AsyncSessionLocal


@asynccontextmanager
async def get_task_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def run_async(coro):
    return asyncio.run(coro)
