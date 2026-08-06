from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.crud import user as crud_user
from app.models import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_me(
    user_in: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if user_in.email is not None and user_in.email != current_user.email:
        existing = await crud_user.get_by_email(db, user_in.email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )
    return await crud_user.update(db, current_user, user_in)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    user = await crud_user.get_or_404(db, user_id)
    return user
