from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

from app.crud.base import CRUDBase
from app.models import Answer, Question, Quiz, QuizAttempt, QuizQuestion
from app.schemas.quiz import QuizCreate, QuizUpdate


class CRUDQuiz(CRUDBase[Quiz, QuizCreate, QuizUpdate]):
    async def get_question_ids(self, db: AsyncSession, quiz_id: UUID) -> list[UUID]:
        result = await db.exec(
            select(QuizQuestion.question_id)
            .where(QuizQuestion.quiz_id == quiz_id)
            .order_by(QuizQuestion.position)
        )
        return list(result.all())

    async def remove(self, db: AsyncSession, id: UUID) -> Quiz | None:
        quiz = await self.get(db, id)
        if quiz is None:
            return None
        attempt_ids = (
            await db.exec(select(QuizAttempt.id).where(QuizAttempt.quiz_id == id))
        ).all()
        for attempt_id in attempt_ids:
            await db.exec(delete(Answer).where(Answer.attempt_id == attempt_id))
        await db.exec(delete(QuizAttempt).where(QuizAttempt.quiz_id == id))
        await db.exec(delete(QuizQuestion).where(QuizQuestion.quiz_id == id))
        await db.delete(quiz)
        await db.commit()
        return quiz

    async def link_question(
        self,
        db: AsyncSession,
        quiz_id: UUID,
        question_id: UUID,
        position: int = 0,
    ) -> QuizQuestion:
        await self.get_or_404(db, quiz_id)
        question = await db.get(Question, question_id)
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )
        existing = await db.exec(
            select(QuizQuestion).where(
                QuizQuestion.quiz_id == quiz_id,
                QuizQuestion.question_id == question_id,
            )
        )
        if existing.first() is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Question already linked to this quiz",
            )
        link = QuizQuestion(quiz_id=quiz_id, question_id=question_id, position=position)
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link

    async def unlink_question(
        self,
        db: AsyncSession,
        quiz_id: UUID,
        question_id: UUID,
    ) -> None:
        await db.exec(
            delete(QuizQuestion).where(
                QuizQuestion.quiz_id == quiz_id,
                QuizQuestion.question_id == question_id,
            )
        )
        await db.commit()


quiz = CRUDQuiz(Quiz)
