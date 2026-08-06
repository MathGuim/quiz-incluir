from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import field_validator
from sqlmodel import SQLModel

from app.models import QuestionType
from app.schemas.media import MediaRead


class QuestionBase(SQLModel):
    type: QuestionType
    prompt: str
    suggested_score: float = 1.0
    config: dict[str, Any] = {}


class QuestionCreate(QuestionBase):
    @field_validator("config", mode="before")
    @classmethod
    def ensure_config_dict(cls, v: Any) -> dict[str, Any]:
        if v is None:
            return {}
        if not isinstance(v, dict):
            raise ValueError("config must be an object")
        return v


class QuestionUpdate(SQLModel):
    type: QuestionType | None = None
    prompt: str | None = None
    suggested_score: float | None = None
    config: dict[str, Any] | None = None


class QuestionRead(QuestionBase):
    id: UUID
    created_at: datetime
    media: list[MediaRead] = []
