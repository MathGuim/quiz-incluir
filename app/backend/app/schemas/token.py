from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel

from quiz_shared.schemas import TokenRead as Token

__all__ = ["Token", "TokenData"]


class TokenData(SQLModel):
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    exp: Optional[datetime] = None
