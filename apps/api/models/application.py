import enum
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.core.database import Base
from apps.api.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ApplicationStatus(str, enum.Enum):
    draft = "draft"
    queued = "queued"
    submitted = "submitted"
    viewed = "viewed"
    interview = "interview"
    rejected = "rejected"
    offer = "offer"
    withdrawn = "withdrawn"


class Application(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_application_user_job"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_postings.id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.queued,
    )
    tailored_resume_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    applied_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped["User"] = relationship("User", back_populates="applications")
    job: Mapped["JobPosting"] = relationship("JobPosting", back_populates="applications")
