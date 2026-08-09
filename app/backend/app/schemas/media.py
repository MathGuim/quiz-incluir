from uuid import UUID

from sqlmodel import SQLModel

from app.models import MediaType
from quiz_shared.schemas import MediaRead, QuizMediaRead

__all__ = [
    "MediaBase",
    "MediaCreate",
    "MediaUpdate",
    "MediaRead",
    "QuizMediaCreate",
    "QuizMediaUpdate",
    "QuizMediaRead",
]


class MediaBase(SQLModel):
    type: MediaType
    url: str | None = None
    caption: str | None = None
    position: int = 0


class MediaCreate(MediaBase):
    question_id: UUID


class MediaUpdate(SQLModel):
    type: MediaType | None = None
    url: str | None = None
    caption: str | None = None
    position: int | None = None


class QuizMediaCreate(MediaBase):
    quiz_id: UUID


class QuizMediaUpdate(SQLModel):
    type: MediaType | None = None
    url: str | None = None
    caption: str | None = None
    position: int | None = None
