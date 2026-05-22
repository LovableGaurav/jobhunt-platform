from apps.api.services.matcher import MatcherService
from apps.api.repositories.job_repo import JobRepository
from workers.celery_app import celery_app
from workers.db import get_task_session, run_async


async def _embed_jobs() -> int:
    embedded = 0
    async with get_task_session() as session:
        repo = JobRepository(session)
        matcher = MatcherService(session)
        pending = await repo.list_without_embedding(limit=50)
        for job in pending:
            try:
                await matcher.embed_job(job)
                embedded += 1
            except Exception:
                continue
    return embedded


@celery_app.task(name="workers.processors.embedder.embed_pending_jobs")
def embed_pending_jobs() -> dict[str, int]:
    count = run_async(_embed_jobs())
    return {"embedded": count}
