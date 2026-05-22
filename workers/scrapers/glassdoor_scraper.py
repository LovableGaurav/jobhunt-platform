from datetime import datetime, timezone
from typing import Any, List

from workers.celery_app import celery_app
from workers.scrapers.base_scraper import HttpxScraper
from apps.api.models.job_posting import JobSource


class GlassdoorScraper(HttpxScraper):
    """Glassdoor requires anti-bot handling; stub with curated fallback."""

    source = JobSource.glassdoor

    async def fetch_raw_jobs(self) -> List[dict[str, Any]]:
        return [
            {
                "external_id": "gd-sample-fe",
                "title": "Junior Frontend Developer",
                "company": "WebCo",
                "location": "Hybrid — Austin, TX",
                "description": (
                    "Junior frontend developer. Hybrid flexible. React, TypeScript. "
                    "Entry level, 0-2 years."
                ),
                "url": "https://glassdoor.com/job/sample",
                "posted_at": datetime.now(timezone.utc),
            },
        ]


@celery_app.task(name="workers.scrapers.glassdoor_scraper.scrape_glassdoor")
def scrape_glassdoor() -> dict[str, int]:
    return GlassdoorScraper().run_sync()
