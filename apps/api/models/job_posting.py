import enum
from datetime import datetime
from typing import Any, List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.core.config import get_settings
from apps.api.core.database import Base
from apps.api.models.base import TimestampMixin, UUIDPrimaryKeyMixin

settings = get_settings()


class WorkMode(str, enum.Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"


class ExperienceLevel(str, enum.Enum):
    entry = "entry"
    junior = "junior"
    mid = "mid"
    senior = "senior"


class JobSource(str, enum.Enum):
    linkedin = "linkedin"
    indeed = "indeed"
    glassdoor = "glassdoor"
    wellfound = "wellfound"


class JobPosting(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "job_postings"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_job_source_external"),
    )

    external_id: Mapped[str] = mapped_column(String(255), index=True)
    source: Mapped[JobSource] = mapped_column(Enum(JobSource), index=True)
    title: Mapped[str] = mapped_column(String(512))
    company: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255), default="")
    work_mode: Mapped[WorkMode] = mapped_column(Enum(WorkMode), default=WorkMode.remote)
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel),
        default=ExperienceLevel.entry,
    )
    description: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(1024))
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parsed_jd: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    embedding: Mapped[Optional[list]] = mapped_column(
        Vector(settings.embedding_dimensions),
        nullable=True,
    )

    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="job",
    )
