from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(SQLModel):
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    exp: Optional[datetime] = None
