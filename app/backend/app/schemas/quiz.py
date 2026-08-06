from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from app.models import LanguageLevel, QuizCategory


class QuizBase(SQLModel):
    title: str
    description: str | None = None
    category: QuizCategory = QuizCategory.READING
    level: LanguageLevel = LanguageLevel.A1


class QuizCreate(QuizBase):
    pass


class QuizUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    category: QuizCategory | None = None
    level: LanguageLevel | None = None


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
    category: QuizCategory
    level: LanguageLevel
    created_at: datetime
    updated_at: datetime
    question_ids: list[UUID] = []


class QuizDetail(QuizRead):
    pass
