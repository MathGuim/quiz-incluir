from pydantic import EmailStr, Field
from sqlmodel import SQLModel

from app.models import LanguageLevel
from quiz_shared.schemas import UserRead

__all__ = ["UserBase", "UserCreate", "UserRead", "UserUpdate", "UserLevelUpdate"]


class UserBase(SQLModel):
    email: EmailStr
    level: LanguageLevel = LanguageLevel.A1


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    email: EmailStr | None = None
    level: LanguageLevel | None = None


class UserLevelUpdate(SQLModel):
    level: LanguageLevel = Field(description="New language level for the user")
