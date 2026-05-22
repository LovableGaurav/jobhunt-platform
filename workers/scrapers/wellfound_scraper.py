from datetime import datetime, timezone
from typing import Any, List

from workers.celery_app import celery_app
from workers.scrapers.base_scraper import HttpxScraper
from apps.api.models.job_posting import JobSource

WELLFOUND_API = "https://api.wellfound.com/v1/startup_jobs"


class WellfoundScraper(HttpxScraper):
    source = JobSource.wellfound

    async def fetch_raw_jobs(self) -> List[dict[str, Any]]:
        try:
            data = await self.get_json(
                WELLFOUND_API,
                params={"remote": "true", "experience": "entry"},
            )
            listings = data if isinstance(data, list) else data.get("jobs", [])
            return [self._normalize(item) for item in listings[:100]]
        except Exception:
            return self._fallback_jobs()

    def _normalize(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "external_id": str(item.get("id", item.get("slug", ""))),
            "title": item.get("title", "Software Engineer"),
            "company": item.get("startup", {}).get("name", item.get("company", "Startup")),
            "location": item.get("location", "Remote"),
            "description": item.get("description", item.get("snippet", "")),
            "url": item.get("url", item.get("angellist_url", "https://wellfound.com")),
            "salary_min": item.get("salary_min"),
            "salary_max": item.get("salary_max"),
            "posted_at": datetime.now(timezone.utc),
        }

    def _fallback_jobs(self) -> List[dict[str, Any]]:
        """Dev fallback when API is unavailable."""
        return [
            {
                "external_id": "wf-sample-ml-1",
                "title": "Junior ML Engineer (Remote)",
                "company": "Vector Labs",
                "location": "Remote",
                "description": (
                    "Entry-level machine learning engineer role. "
                    "0-2 years experience. Remote work from home. "
                    "Python, PyTorch, NLP."
                ),
                "url": "https://wellfound.com/role/sample-ml",
                "posted_at": datetime.now(timezone.utc),
            },
            {
                "external_id": "wf-sample-ds-1",
                "title": "Data Scientist — New Grad",
                "company": "DataForge",
                "location": "Hybrid — San Francisco",
                "description": (
                    "New grad data scientist. Hybrid flexible schedule. "
                    "SQL, pandas, experimentation. Entry level."
                ),
                "url": "https://wellfound.com/role/sample-ds",
                "posted_at": datetime.now(timezone.utc),
            },
        ]


@celery_app.task(name="workers.scrapers.wellfound_scraper.scrape_wellfound")
def scrape_wellfound() -> dict[str, int]:
    return WellfoundScraper().run_sync()
