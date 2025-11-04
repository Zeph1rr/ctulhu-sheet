"""
Базовый CRUD-сервис для SQLModel с внедрением асинхронной сессии через Depends.
"""

from typing import Type, TypeVar, Generic, Optional, Sequence, Any, Dict
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import Depends

from ..db import get_async_session

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)


class BaseService(Generic[ModelType, CreateSchemaType]):
    """Базовый сервис с CRUD-методами и внедрением асинхронной сессии."""

    def __init__(self, model: Type[ModelType], session: AsyncSession = Depends(get_async_session)):
        self.model = model
        self.session = session

    async def get(self, obj_id: Any) -> Optional[ModelType]:
        """Получить объект по ID."""
        return await self.session.get(self.model, obj_id)

    async def get_multi(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Получить несколько объектов."""
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Создать объект."""
        obj = self.model(**obj_in.model_dump())
        self.session.add(obj)
        try:
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except IntegrityError:
            await self.session.rollback()
            raise

    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Обновить объект."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, obj_id: Any) -> None:
        """Удалить объект по ID."""
        obj = await self.get(obj_id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()