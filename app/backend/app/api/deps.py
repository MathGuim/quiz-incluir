from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_token
from app.models import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token",
    auto_error=False,
)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    token_data = verify_token(token)
    if token_data is None or token_data.user_id is None:
        raise credentials_exception

    result = await db.exec(select(User).where(User.id == token_data.user_id))
    user = result.first()
    if user is None:
        raise credentials_exception
    return user


async def get_optional_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
) -> Optional[User]:
    if not token:
        return None
    token_data = verify_token(token)
    if token_data is None or token_data.user_id is None:
        return None
    result = await db.exec(select(User).where(User.id == token_data.user_id))
    return result.first()
