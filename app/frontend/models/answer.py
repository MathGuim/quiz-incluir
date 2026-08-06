"""Answer model matching backend AnswerRead."""

from __future__ import annotations

from pydantic import BaseModel


class AnswerRead(BaseModel):
    id: str
    attempt_id: str
    question_id: str
    response: dict = {}
    is_correct: bool | None = None
    points_awarded: float = 0.0