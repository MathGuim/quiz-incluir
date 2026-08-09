from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.core.grading import grade_question
from app.core.pdf_report import ReportRow
from app.crud.base import CRUDBase
from app.models import Answer, Question, Quiz, QuizAttempt, QuizQuestion, User
from app.schemas.answer import AnswerSubmit
from app.schemas.attempt import AttemptStart


class CRUDAttempt(CRUDBase[QuizAttempt, AttemptStart, None]):
    async def start(self, db: AsyncSession, user: User, quiz_id: UUID) -> QuizAttempt:
        quiz = await db.get(Quiz, quiz_id)
        if quiz is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quiz not found",
            )
        attempt = QuizAttempt(quiz_id=quiz_id, user_id=user.id)
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        return attempt

    async def get_max_score(self, db: AsyncSession, quiz_id: UUID) -> float:
        from app.models import QuizQuestion

        result = await db.exec(
            select(Question.suggested_score)
            .join(QuizQuestion, QuizQuestion.question_id == Question.id)
            .where(QuizQuestion.quiz_id == quiz_id)
        )
        return float(sum(result.all()))

    async def submit_answer(
        self,
        db: AsyncSession,
        attempt: QuizAttempt,
        answer_in: AnswerSubmit,
    ) -> Answer:
        question = await db.get(Question, answer_in.question_id)
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found",
            )
        is_correct = grade_question(question, answer_in.response)
        points = question.suggested_score if is_correct else 0.0
        existing = await db.exec(
            select(Answer).where(
                Answer.attempt_id == attempt.id,
                Answer.question_id == answer_in.question_id,
            )
        )
        existing_answer = existing.first()
        if existing_answer is not None:
            existing_answer.response = answer_in.response
            existing_answer.is_correct = is_correct
            existing_answer.points_awarded = points
            db.add(existing_answer)
            await db.commit()
            await db.refresh(existing_answer)
            return existing_answer

        answer = Answer(
            attempt_id=attempt.id,
            question_id=answer_in.question_id,
            response=answer_in.response,
            is_correct=is_correct,
            points_awarded=points,
        )
        db.add(answer)
        await db.commit()
        await db.refresh(answer)
        return answer

    async def finish(self, db: AsyncSession, attempt: QuizAttempt) -> QuizAttempt:
        from datetime import datetime, UTC

        if attempt.finished_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attempt already finished",
            )
        result = await db.exec(
            select(Answer).where(Answer.attempt_id == attempt.id)
        )
        answers = list(result.all())
        attempt.score = sum(a.points_awarded for a in answers)
        attempt.finished_at = datetime.now(UTC)
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        return attempt

    async def get_answers(self, db: AsyncSession, attempt_id: UUID) -> list[Answer]:
        result = await db.exec(
            select(Answer).where(Answer.attempt_id == attempt_id)
        )
        return list(result.all())

    async def get_report_rows(
        self, db: AsyncSession, attempt: QuizAttempt
    ) -> tuple[Quiz, list[ReportRow]]:
        quiz = await db.get(Quiz, attempt.quiz_id, options=[selectinload(Quiz.media)])

        result = await db.exec(
            select(Question)
            .join(QuizQuestion, QuizQuestion.question_id == Question.id)
            .where(QuizQuestion.quiz_id == attempt.quiz_id)
            .options(selectinload(Question.media))
            .order_by(QuizQuestion.position)
        )
        questions = list(result.all())

        answers_by_question = {
            answer.question_id: answer
            for answer in await self.get_answers(db, attempt.id)
        }

        rows = [
            ReportRow(
                question=question,
                media=list(question.media),
                answer=answers_by_question.get(question.id),
            )
            for question in questions
        ]
        return quiz, rows


attempt = CRUDAttempt(QuizAttempt)
