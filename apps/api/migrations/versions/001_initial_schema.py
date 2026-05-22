"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("target_roles", postgresql.ARRAY(sa.String()), server_default="{}"),
        sa.Column("years_experience", sa.Integer(), server_default="0"),
        sa.Column("resume_s3_key", sa.String(512), nullable=True),
        sa.Column("resume_text", sa.Text(), nullable=True),
        sa.Column("resume_embedding", Vector(1536), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    job_source = postgresql.ENUM(
        "linkedin", "indeed", "glassdoor", "wellfound",
        name="jobsource",
        create_type=False,
    )
    work_mode = postgresql.ENUM(
        "remote", "hybrid", "onsite", name="workmode", create_type=False
    )
    experience_level = postgresql.ENUM(
        "entry", "junior", "mid", "senior",
        name="experiencelevel",
        create_type=False,
    )
    job_source.create(op.get_bind(), checkfirst=True)
    work_mode.create(op.get_bind(), checkfirst=True)
    experience_level.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "job_postings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(255), nullable=False),
        sa.Column("source", job_source, nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), server_default=""),
        sa.Column("work_mode", work_mode, nullable=False),
        sa.Column("experience_level", experience_level, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "scraped_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("parsed_jd", postgresql.JSONB(), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("source", "external_id", name="uq_job_source_external"),
    )
    op.create_index("ix_job_postings_external_id", "job_postings", ["external_id"])
    op.create_index("ix_job_postings_source", "job_postings", ["source"])

    app_status = postgresql.ENUM(
        "draft", "queued", "submitted", "viewed", "interview",
        "rejected", "offer", "withdrawn",
        name="applicationstatus",
        create_type=False,
    )
    app_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", app_status, nullable=False),
        sa.Column("tailored_resume_key", sa.String(512), nullable=True),
        sa.Column("cover_letter", sa.Text(), nullable=True),
        sa.Column("match_score", sa.Float(), server_default="0"),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["job_postings.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "job_id", name="uq_application_user_job"),
    )

    scraper_status = postgresql.ENUM(
        "running", "success", "failed", name="scraperstatus", create_type=False
    )
    scraper_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "scraper_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", job_source, nullable=False),
        sa.Column("status", scraper_status, nullable=False),
        sa.Column("jobs_found", sa.Integer(), server_default="0"),
        sa.Column("jobs_saved", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("scraper_logs")
    op.drop_table("applications")
    op.drop_table("job_postings")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS scraperstatus")
    op.execute("DROP TYPE IF EXISTS applicationstatus")
    op.execute("DROP TYPE IF EXISTS experiencelevel")
    op.execute("DROP TYPE IF EXISTS workmode")
    op.execute("DROP TYPE IF EXISTS jobsource")
