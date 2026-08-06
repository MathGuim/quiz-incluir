from uuid import UUID

from sqlmodel import SQLModel

from app.models import MediaType


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


class MediaRead(MediaBase):
    id: UUID
    question_id: UUID
