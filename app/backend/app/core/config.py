from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
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
        default="sqlite+aiosqlite:///./quiz.db",
        description="Async database URL",
    )

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