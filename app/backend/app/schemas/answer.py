from datetime import datetime
from typing import Any
from uuid import UUID

from sqlmodel import SQLModel


class AnswerCreate(SQLModel):
    question_id: UUID
    response: dict[str, Any] = {}


class AnswerSubmit(AnswerCreate):
    pass


class AnswerRead(SQLModel):
    id: UUID
    attempt_id: UUID
    question_id: UUID
    response: dict[str, Any]
    is_correct: bool | None = None
    points_awarded: float
    answered_at: datetime


class AnswerUpdate(SQLModel):
    response: dict[str, Any] | None = None
