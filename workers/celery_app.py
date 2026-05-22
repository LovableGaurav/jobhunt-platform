import os
import sys
from pathlib import Path

# Project root on PYTHONPATH for apps.api imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from celery import Celery

from apps.api.core.config import get_settings
from workers.beat_schedule import beat_schedule

settings = get_settings()

celery_app = Celery(
    "jobhunt",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "workers.scrapers.wellfound_scraper",
        "workers.scrapers.indeed_scraper",
        "workers.scrapers.linkedin_scraper",
        "workers.processors.jd_parser",
        "workers.processors.embedder",
        "workers.processors.notifier",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule=beat_schedule,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)
