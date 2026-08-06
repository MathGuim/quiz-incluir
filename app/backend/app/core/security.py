from datetime import datetime, timedelta, UTC
from typing import Optional
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    exp: Optional[datetime] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        exp_timestamp: int = payload.get("exp")
        if user_id is None:
            return None
        return TokenData(
            user_id=UUID(user_id),
            email=email,
            exp=datetime.fromtimestamp(exp_timestamp, UTC) if exp_timestamp else None,
        )
    except (JWTError, ValueError):
        return None


def create_token_for_user(user_id: UUID, email: str) -> str:
    return create_access_token(
        data={"sub": str(user_id), "email": email},
    )