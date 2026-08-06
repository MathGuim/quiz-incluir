from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import answer as crud_answer
from app.models import Answer, QuizAttempt, User
from app.schemas.answer import AnswerRead

router = APIRouter()


@router.get("", response_model=list[AnswerRead])
async def list_answers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    attempt_id: UUID | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Answer]:
    stmt = select(Answer).order_by(Answer.answered_at)
    if attempt_id:
        stmt = stmt.where(Answer.attempt_id == attempt_id)
    result = await db.exec(stmt.offset(skip).limit(limit))
    return list(result.all())


@router.get("/{answer_id}", response_model=AnswerRead)
async def read_answer(
    answer_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Answer:
    answer = await crud_answer.get_or_404(db, answer_id)
    attempt = await db.get(QuizAttempt, answer.attempt_id)
    if attempt is None or attempt.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view this answer",
        )
    return answer
