from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

from app.crud.base import CRUDBase
from app.models import Answer, Question, QuestionMedia, QuizQuestion
from app.schemas.question import QuestionCreate, QuestionUpdate


class CRUDQuestion(CRUDBase[Question, QuestionCreate, QuestionUpdate]):
    async def remove(self, db: AsyncSession, id: UUID) -> Question | None:
        question = await self.get(db, id)
        if question is None:
            return None

        answer = (
            await db.exec(select(Answer.id).where(Answer.question_id == id).limit(1))
        ).first()
        if answer is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Question is referenced by attempts and cannot be deleted",
            )

        await db.exec(delete(QuestionMedia).where(QuestionMedia.question_id == id))
        await db.exec(delete(QuizQuestion).where(QuizQuestion.question_id == id))
        await db.delete(question)
        await db.commit()
        return question


question = CRUDQuestion(Question)
