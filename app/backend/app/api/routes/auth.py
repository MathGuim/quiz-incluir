from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.oauth2 import get_google_user_info, handle_google_callback, redirect_to_google
from app.core.security import create_token_for_user
from app.crud import user as crud_user
from app.models import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


async def _create_user_for_email(db: AsyncSession, email: str) -> User:
    try:
        return await crud_user.create(db, UserCreate(email=email))
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please enter a valid email address",
        )


@router.get("/login", response_model=dict)
async def login(request: Request) -> RedirectResponse:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth2 is not configured",
        )
    return await redirect_to_google(request)


@router.get("/callback", response_model=Token)
async def callback(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth2 is not configured",
        )
    try:
        google_user = await handle_google_callback(request)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google OAuth2 authentication failed",
        )

    info = get_google_user_info(google_user)
    email = info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account has no email",
        )

    db_user = await crud_user.get_by_email(db, email)
    if db_user is None:
        db_user = await _create_user_for_email(db, email)

    token = create_token_for_user(db_user.id, db_user.email)
    return Token(access_token=token)


@router.post("/token", response_model=Token)
async def token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
):
    email = form_data.username.strip().lower()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="username (email) is required",
        )
    db_user = await crud_user.get_by_email(db, email)
    if db_user is None:
        db_user = await _create_user_for_email(db, email)
    token = create_token_for_user(db_user.id, db_user.email)
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
async def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
