import re
from typing import Any, Optional

from apps.api.models.job_posting import ExperienceLevel, JobPosting, WorkMode

ENTRY_KEYWORDS = re.compile(
    r"\b(entry[- ]?level|new grad|graduate|junior|0[- ]?2 years?|"
    r"0[- ]?1 years?|intern(?:ship)?|associate|fresher)\b",
    re.IGNORECASE,
)
SENIOR_BLOCK = re.compile(
    r"\b(senior|staff|principal|lead|architect|10\+ years?|8\+ years?)\b",
    re.IGNORECASE,
)
REMOTE_KEYWORDS = re.compile(
    r"\b(remote|work from home|wfh|distributed)\b",
    re.IGNORECASE,
)
HYBRID_KEYWORDS = re.compile(r"\b(hybrid|flexible)\b", re.IGNORECASE)
TARGET_ROLES = re.compile(
    r"\b(machine learning|ml engineer|data scien|software engineer|"
    r"backend|frontend|full[- ]?stack|developer)\b",
    re.IGNORECASE,
)


class JobFilterService:
    """Multi-layer filter: entry-level, remote/hybrid, target role keywords."""

    def __init__(
        self,
        allowed_work_modes: Optional[list[WorkMode]] = None,
        allowed_experience: Optional[list[ExperienceLevel]] = None,
    ):
        self.allowed_work_modes = allowed_work_modes or [
            WorkMode.remote,
            WorkMode.hybrid,
        ]
        self.allowed_experience = allowed_experience or [
            ExperienceLevel.entry,
            ExperienceLevel.junior,
        ]

    def passes_structured_filters(self, job: JobPosting) -> bool:
        if job.work_mode not in self.allowed_work_modes:
            return False
        if job.experience_level not in self.allowed_experience:
            return False
        return True

    def score_text(self, title: str, description: str) -> float:
        text = f"{title}\n{description}"
        if SENIOR_BLOCK.search(text):
            return 0.0
        score = 0.0
        if ENTRY_KEYWORDS.search(text):
            score += 0.5
        if REMOTE_KEYWORDS.search(text) or HYBRID_KEYWORDS.search(text):
            score += 0.25
        if TARGET_ROLES.search(text):
            score += 0.25
        return min(score, 1.0)

    def should_keep(self, job: JobPosting) -> bool:
        if not self.passes_structured_filters(job):
            return False
        return self.score_text(job.title, job.description) >= 0.5

    def classify_from_raw(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Infer work_mode and experience_level from scraped raw payload."""
        text = f"{raw.get('title', '')} {raw.get('description', '')} {raw.get('location', '')}"
        work_mode = WorkMode.onsite
        if REMOTE_KEYWORDS.search(text):
            work_mode = WorkMode.remote
        elif HYBRID_KEYWORDS.search(text):
            work_mode = WorkMode.hybrid

        experience_level = ExperienceLevel.entry
        if SENIOR_BLOCK.search(text):
            experience_level = ExperienceLevel.senior
        elif not ENTRY_KEYWORDS.search(text):
            experience_level = ExperienceLevel.junior

        return {
            "work_mode": work_mode,
            "experience_level": experience_level,
        }
