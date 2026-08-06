"""Question model matching backend QuestionRead + QuestionType enum."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

from models.media import Media


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    MULTIPLE_SELECTION = "multiple_selection"
    TRUE_FALSE = "true_false"
    SHORT_TEXT = "short_text"


class Question(BaseModel):
    id: str
    type: QuestionType
    prompt: str
    suggested_score: float = 1.0
    config: dict = {}
    media: list[Media] = []

    @property
    def options(self) -> list[str]:
        return (self.config or {}).get("options", [])