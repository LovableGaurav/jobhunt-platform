import json
from typing import Any

from openai import OpenAI

from apps.api.core.config import get_settings
from apps.api.repositories.job_repo import JobRepository
from workers.celery_app import celery_app
from workers.db import get_task_session, run_async

settings = get_settings()


async def _parse_jobs() -> int:
    if not settings.openai_api_key:
        return 0

    client = OpenAI(api_key=settings.openai_api_key)
    parsed = 0

    async with get_task_session() as session:
        repo = JobRepository(session)
        jobs = await repo.list_active(limit=50)
        for job in jobs:
            if job.parsed_jd:
                continue
            prompt = f"""Extract structured fields from this job description.
Return JSON with keys: skills (array), education (string), years_required (string), remote_policy (string).

Job: {job.title} at {job.company}
{job.description[:3500]}"""

            try:
                resp = client.chat.completions.create(
                    model=settings.openai_chat_model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0,
                )
                job.parsed_jd = json.loads(resp.choices[0].message.content or "{}")
                parsed += 1
            except Exception:
                job.parsed_jd = {"error": "parse_failed"}
            await session.flush()

    return parsed


@celery_app.task(name="workers.processors.jd_parser.parse_pending_jds")
def parse_pending_jds() -> dict[str, int]:
    count = run_async(_parse_jobs())
    return {"parsed": count}
