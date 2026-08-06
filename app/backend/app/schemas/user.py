from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field
from sqlmodel import SQLModel

from app.models import LanguageLevel


class UserBase(SQLModel):
    email: EmailStr
    level: LanguageLevel = LanguageLevel.A1


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UserUpdate(SQLModel):
    email: EmailStr | None = None
    level: LanguageLevel | None = None


class UserLevelUpdate(SQLModel):
    level: LanguageLevel = Field(description="New language level for the user")
