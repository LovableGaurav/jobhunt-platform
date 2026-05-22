import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.database import Base
from apps.api.models.base import UUIDPrimaryKeyMixin
from apps.api.models.job_posting import JobSource


class ScraperStatus(str, enum.Enum):
    running = "running"
    success = "success"
    failed = "failed"


class ScraperLog(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "scraper_logs"

    source: Mapped[JobSource] = mapped_column(Enum(JobSource))
    status: Mapped[ScraperStatus] = mapped_column(
        Enum(ScraperStatus),
        default=ScraperStatus.running,
    )
    jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    jobs_saved: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
