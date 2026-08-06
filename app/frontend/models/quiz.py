"""Quiz model matching backend QuizRead."""

from __future__ import annotations

from pydantic import BaseModel


class Quiz(BaseModel):
    id: str
    title: str
    description: str | None = None
    category: str | None = None
    level: str | None = None
    question_ids: list[str] = []