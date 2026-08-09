from typing import Any
from uuid import UUID

from sqlmodel import SQLModel

from quiz_shared.schemas import AnswerRead

__all__ = ["AnswerCreate", "AnswerSubmit", "AnswerRead", "AnswerUpdate"]


class AnswerCreate(SQLModel):
    question_id: UUID
    response: dict[str, Any] = {}


class AnswerSubmit(AnswerCreate):
    pass


class AnswerUpdate(SQLModel):
    response: dict[str, Any] | None = None
