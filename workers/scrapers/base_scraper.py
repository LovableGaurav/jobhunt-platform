import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, List, Optional

import httpx

from apps.api.core.config import get_settings
from apps.api.models.job_posting import JobPosting, JobSource
from apps.api.models.scraper_log import ScraperLog, ScraperStatus
from apps.api.repositories.job_repo import JobRepository
from apps.api.services.job_filter import JobFilterService
from workers.db import get_task_session, run_async

settings = get_settings()


class BaseScraper(ABC):
    source: JobSource
    max_retries: int = 3

    def __init__(self):
        self.filter = JobFilterService()
        self._proxy = settings.brightdata_proxy_url or None

    def _client_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "timeout": 30.0,
            "headers": {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; JobHuntBot/1.0; +https://jobhunt.local)"
                ),
            },
        }
        if self._proxy:
            kwargs["proxy"] = self._proxy
        return kwargs

    @abstractmethod
    async def fetch_raw_jobs(self) -> List[dict[str, Any]]:
        """Return normalized raw job dicts from the source."""

    def raw_to_model(self, raw: dict[str, Any]) -> JobPosting:
        classified = self.filter.classify_from_raw(raw)
        return JobPosting(
            external_id=str(raw["external_id"]),
            source=self.source,
            title=raw["title"],
            company=raw.get("company", "Unknown"),
            location=raw.get("location", ""),
            work_mode=classified["work_mode"],
            experience_level=classified["experience_level"],
            description=raw.get("description", ""),
            url=raw["url"],
            salary_min=raw.get("salary_min"),
            salary_max=raw.get("salary_max"),
            posted_at=raw.get("posted_at") or datetime.now(timezone.utc),
            parsed_jd=raw.get("parsed_jd"),
        )

    async def run(self) -> dict[str, int]:
        async with get_task_session() as session:
            log = ScraperLog(source=self.source, status=ScraperStatus.running)
            session.add(log)
            await session.flush()

            found = 0
            saved = 0
            try:
                raw_jobs = await self.fetch_raw_jobs()
                found = len(raw_jobs)
                repo = JobRepository(session)
                for raw in raw_jobs:
                    job = self.raw_to_model(raw)
                    if not self.filter.should_keep(job):
                        continue
                    _, created = await repo.upsert(job)
                    if created:
                        saved += 1
                log.status = ScraperStatus.success
            except Exception as exc:
                log.status = ScraperStatus.failed
                log.error_message = str(exc)[:2000]
                raise
            finally:
                log.jobs_found = found
                log.jobs_saved = saved
                log.finished_at = datetime.now(timezone.utc)
                await session.flush()

            return {"found": found, "saved": saved}

    def run_sync(self) -> dict[str, int]:
        return run_async(self.run())


async def _retry_fetch(coro_factory, retries: int = 3) -> Any:
    last_exc: Optional[Exception] = None
    for attempt in range(retries):
        try:
            return await coro_factory()
        except Exception as exc:
            last_exc = exc
            await asyncio.sleep(2**attempt)
    raise last_exc  # type: ignore[misc]


class HttpxScraper(BaseScraper):
    async def get_json(self, url: str, params: Optional[dict] = None) -> Any:
        async def _do():
            async with httpx.AsyncClient(**self._client_kwargs()) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()

        return await _retry_fetch(_do, self.max_retries)
