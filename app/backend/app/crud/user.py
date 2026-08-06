from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.crud.base import CRUDBase
from app.models import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        result = await db.exec(select(User).where(User.email == email))
        return result.first()


user = CRUDUser(User)
