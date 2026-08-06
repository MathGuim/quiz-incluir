from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class QuizBase(SQLModel):
    title: str
    description: str | None = None


class QuizCreate(QuizBase):
    pass


class QuizUpdate(SQLModel):
    title: str | None = None
    description: str | None = None


class QuizQuestionLinkCreate(SQLModel):
    question_id: UUID
    position: int = 0


class QuizQuestionLink(SQLModel):
    quiz_id: UUID
    question_id: UUID
    position: int


class QuizRead(SQLModel):
    id: UUID
    title: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
    question_ids: list[UUID] = []


class QuizDetail(QuizRead):
    pass
