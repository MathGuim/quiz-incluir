from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.crud.base import CRUDBase
from app.models import Answer
from app.schemas.answer import AnswerCreate, AnswerUpdate


class CRUDAnswer(CRUDBase[Answer, AnswerCreate, AnswerUpdate]):
    async def list_by_attempt(self, db: AsyncSession, attempt_id: UUID) -> list[Answer]:
        result = await db.exec(select(Answer).where(Answer.attempt_id == attempt_id))
        return list(result.all())


answer = CRUDAnswer(Answer)
