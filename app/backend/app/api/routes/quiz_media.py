from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import quiz_media as crud_quiz_media
from app.models import QuizMedia, User
from app.schemas.media import QuizMediaCreate, QuizMediaRead, QuizMediaUpdate

router = APIRouter()


@router.get("", response_model=list[QuizMediaRead])
async def list_quiz_media(
    db: Annotated[AsyncSession, Depends(get_db)],
    quiz_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[QuizMedia]:
    stmt = select(QuizMedia).order_by(QuizMedia.position)
    if quiz_id:
        try:
            qid = UUID(quiz_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="quiz_id must be a valid UUID",
            )
        stmt = stmt.where(QuizMedia.quiz_id == qid)
    result = await db.exec(stmt.offset(skip).limit(limit))
    return list(result.all())


@router.post("", response_model=QuizMediaRead, status_code=status.HTTP_201_CREATED)
async def create_quiz_media(
    media_in: QuizMediaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> QuizMedia:
    return await crud_quiz_media.create(db, media_in)


@router.get("/{media_id}", response_model=QuizMediaRead)
async def read_quiz_media(
    media_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuizMedia:
    return await crud_quiz_media.get_or_404(db, media_id)


@router.patch("/{media_id}", response_model=QuizMediaRead)
async def update_quiz_media(
    media_id: UUID,
    media_in: QuizMediaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> QuizMedia:
    media = await crud_quiz_media.get_or_404(db, media_id)
    return await crud_quiz_media.update(db, media, media_in)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz_media(
    media_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await crud_quiz_media.remove(db, media_id)
