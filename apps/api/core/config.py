from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    database_url: str = Field(
        default="postgresql+asyncpg://jobhunt:jobhunt@localhost:5432/jobhunt",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    secret_key: str = Field(
        default="dev-secret-change-in-production-32bytes!",
        alias="SECRET_KEY",
    )
    access_token_expire_minutes: int = Field(
        default=60 * 24 * 7,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    algorithm: str = "HS256"
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        default="text-embedding-ada-002",
        alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_chat_model: str = Field(default="gpt-4o-mini", alias="OPENAI_CHAT_MODEL")

    aws_access_key_id: str = Field(default="", alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_s3_bucket: str = Field(default="jobhunt-resumes", alias="AWS_S3_BUCKET")

    brightdata_proxy_url: str = Field(default="", alias="BRIGHTDATA_PROXY_URL")
    cors_origins: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS",
    )

    match_score_threshold: float = 0.7
    embedding_dimensions: int = 1536

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
