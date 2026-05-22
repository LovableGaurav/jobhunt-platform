from apps.api.models.job_posting import ExperienceLevel, JobPosting, JobSource, WorkMode
from apps.api.services.job_filter import JobFilterService
from datetime import datetime, timezone


def _job(title: str, description: str, work_mode=WorkMode.remote) -> JobPosting:
    return JobPosting(
        external_id="test-1",
        source=JobSource.wellfound,
        title=title,
        company="Co",
        location="Remote",
        work_mode=work_mode,
        experience_level=ExperienceLevel.entry,
        description=description,
        url="https://example.com",
        posted_at=datetime.now(timezone.utc),
    )


def test_keeps_entry_remote_role():
    filt = JobFilterService()
    job = _job(
        "Junior ML Engineer",
        "Entry level remote machine learning engineer. 0-2 years.",
    )
    assert filt.should_keep(job) is True


def test_rejects_senior_role():
    filt = JobFilterService()
    job = _job(
        "Senior Staff Engineer",
        "10+ years experience required. Principal architect.",
        WorkMode.remote,
    )
    assert filt.should_keep(job) is False


def test_rejects_onsite_only():
    filt = JobFilterService()
    job = _job(
        "Junior Developer",
        "Entry level software engineer.",
        WorkMode.onsite,
    )
    assert filt.should_keep(job) is False
