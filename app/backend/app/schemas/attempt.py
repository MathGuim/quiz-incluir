from uuid import UUID

from sqlmodel import SQLModel

from quiz_shared.schemas import AttemptRead

__all__ = ["AttemptStart", "AttemptRead", "AttemptFinish", "AttemptResult"]


class AttemptStart(SQLModel):
    quiz_id: UUID


class AttemptFinish(SQLModel):
    pass


class AttemptResult(AttemptRead):
    pass
