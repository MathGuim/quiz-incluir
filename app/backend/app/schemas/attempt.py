from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel


class AttemptStart(SQLModel):
    quiz_id: UUID


class AttemptRead(SQLModel):
    id: UUID
    quiz_id: UUID
    user_id: UUID
    started_at: datetime
    finished_at: datetime | None = None
    score: float | None = None
    max_score: float


class AttemptFinish(SQLModel):
    pass


class AttemptResult(AttemptRead):
    pass
