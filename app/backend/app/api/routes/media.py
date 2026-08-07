from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import media as crud_media
from app.models import QuestionMedia, User
from app.schemas.media import MediaCreate, MediaRead, MediaUpdate

router = APIRouter()


@router.get("", response_model=list[MediaRead])
async def list_media(
    db: Annotated[AsyncSession, Depends(get_db)],
    question_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[QuestionMedia]:
    stmt = select(QuestionMedia).order_by(QuestionMedia.position)
    if question_id:
        try:
            qid = UUID(question_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="question_id must be a valid UUID",
            )
        stmt = stmt.where(QuestionMedia.question_id == qid)
    result = await db.exec(stmt.offset(skip).limit(limit))
    return list(result.all())


@router.post("", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
async def create_media(
    media_in: MediaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> QuestionMedia:
    return await crud_media.create(db, media_in)


@router.get("/{media_id}", response_model=MediaRead)
async def read_media(
    media_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> QuestionMedia:
    return await crud_media.get_or_404(db, media_id)


@router.patch("/{media_id}", response_model=MediaRead)
async def update_media(
    media_id: UUID,
    media_in: MediaUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> QuestionMedia:
    media = await crud_media.get_or_404(db, media_id)
    return await crud_media.update(db, media, media_in)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await crud_media.remove(db, media_id)
