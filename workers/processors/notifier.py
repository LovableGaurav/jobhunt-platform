"""Email/push alerts for high-match jobs (stub logs for now)."""
import logging

from apps.api.core.config import get_settings
from apps.api.repositories.user_repo import UserRepository
from apps.api.services.matcher import MatcherService
from workers.celery_app import celery_app
from workers.db import get_task_session, run_async

logger = logging.getLogger(__name__)
settings = get_settings()


async def _notify_users() -> int:
    notified = 0
    async with get_task_session() as session:
        from sqlalchemy import select
        from apps.api.models.user import User

        result = await session.execute(
            select(User).where(User.resume_embedding.is_not(None))
        )
        users = list(result.scalars().all())
        matcher = MatcherService(session)

        for user in users:
            matches = await matcher.get_matches(
                user,
                min_score=settings.match_score_threshold,
                limit=5,
            )
            if matches:
                logger.info(
                    "Match alert for %s: %d jobs (top: %s)",
                    user.email,
                    len(matches),
                    matches[0].title,
                )
                notified += 1
    return notified


@celery_app.task(name="workers.processors.notifier.send_match_alerts")
def send_match_alerts() -> dict[str, int]:
    count = run_async(_notify_users())
    return {"notified": count}
