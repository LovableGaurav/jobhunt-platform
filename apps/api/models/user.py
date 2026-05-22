from typing import List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.core.config import get_settings
from apps.api.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from apps.api.core.database import Base

settings = get_settings()


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    target_roles: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        default=list,
        server_default="{}",
    )
    years_experience: Mapped[int] = mapped_column(Integer, default=0)
    resume_s3_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_embedding: Mapped[Optional[list]] = mapped_column(
        Vector(settings.embedding_dimensions),
        nullable=True,
    )

    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan",
    )
