from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Quiz API"

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/quiz",
        description="Async database URL",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def normalize_db_url(cls, v: str) -> str:
        """Ensure SQLAlchemy async engines get an async driver for Postgres.

        Render injects ``DATABASE_URL`` as ``postgresql://user:pass@host/db``
        (sync scheme). Rewrite it to the asyncpg scheme the app uses.
        """
        if v.startswith("postgres://") or v.startswith("postgresql://"):
            scheme = v.split("://", 1)[0]
            if "+" not in scheme:
                return "postgresql+asyncpg://" + v.split("://", 1)[1]
        return v

    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth2 Client ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", description="Google OAuth2 Client Secret")
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/api/v1/auth/callback", description="Google OAuth2 Redirect URI")

    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", description="JWT Secret Key")
    ALGORITHM: str = Field(default="HS256", description="JWT Algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7, description="Access token expiration in minutes (7 days)")

    FRONTEND_URL: str = Field(default="http://localhost:3000", description="Frontend URL for CORS and OAuth redirects")

    ALL_CORS_ORIGINS: List[str] = Field(default=["*"], description="Allowed CORS origins")

    DEFAULT_USER_LEVEL: str = Field(default="A1", description="Default language level for new users")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()