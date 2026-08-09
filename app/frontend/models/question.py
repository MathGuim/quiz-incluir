"""Question model: shared read-schema plus a UI-convenience ``options`` property."""

from __future__ import annotations

from quiz_shared.enums import QuestionType
from quiz_shared.schemas import QuestionRead

__all__ = ["QuestionType", "Question"]


class Question(QuestionRead):
    @property
    def options(self) -> list[str]:
        return (self.config or {}).get("options", [])
