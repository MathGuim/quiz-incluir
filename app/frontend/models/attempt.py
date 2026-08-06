"""Auth and attempt models matching backend Token/UserRead/AttemptRead."""

from __future__ import annotations

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class User(BaseModel):
    id: str
    email: str
    level: str | None = None


class Attempt(BaseModel):
    id: str
    quiz_id: str
    user_id: str
    started_at: str | None = None
    finished_at: str | None = None
    score: float | None = None
    max_score: float = 0.0


class AttemptResult(Attempt):
    """Alias used by results; structurally identical to Attempt."""