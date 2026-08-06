from typing import Any, Generic, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        return await db.get(self.model, id)

    async def get_or_404(self, db: AsyncSession, id: Any) -> ModelType:
        obj = await self.get(db, id)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} not found",
            )
        return obj

    async def list(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelType]:
        stmt = select(self.model)
        for field, value in (filters or {}).items():
            if value is not None:
                stmt = stmt.where(getattr(self.model, field) == value)
        result = await db.exec(stmt.offset(skip).limit(limit))
        return list(result.all())

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj = self.model.model_validate(obj_in)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None or field in update_data:
                setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, id: Any) -> ModelType | None:
        obj = await self.get(db, id)
        if obj is None:
            return None
        await db.delete(obj)
        await db.commit()
        return obj
