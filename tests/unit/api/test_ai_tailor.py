from datetime import datetime, timezone

from apps.api.models.job_posting import ExperienceLevel, JobPosting, JobSource, WorkMode
from apps.api.models.user import User
from apps.api.services.ai_tailor import AITailorService


def _user() -> User:
    return User(
        email="test@example.com",
        hashed_password="x",
        full_name="Test User",
        resume_text="Built Python APIs at university. 1 year internship.",
    )


def _job() -> JobPosting:
    return JobPosting(
        external_id="j1",
        source=JobSource.wellfound,
        title="ML Engineer",
        company="AI Co",
        location="Remote",
        work_mode=WorkMode.remote,
        experience_level=ExperienceLevel.entry,
        description="Entry level machine learning. Python required.",
        url="https://example.com",
        posted_at=datetime.now(timezone.utc),
    )


def test_tailor_without_openai_returns_fallback():
    import asyncio

    service = AITailorService()
    result = asyncio.run(service.tailor(_user(), _job()))
    assert "ML Engineer" in result["cover_letter"]
    assert result["tailored_resume"]
