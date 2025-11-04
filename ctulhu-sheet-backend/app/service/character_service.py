"""
Сервис для управления персонажами (CharacterService).
"""

from typing import List, Optional
from uuid import UUID
from fastapi import Depends

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.character import Character, CharacterCreate, CharacterUpdate
from ..service.base import BaseService
from ..db import get_async_session
from ..core.errors import NotFoundError, ForbidenError


class CharacterService(BaseService[Character, CharacterCreate]):
    """Сервис управления персонажами пользователей."""

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        super().__init__(Character, session)

    # 🔹 Получить персонажа по ID (с проверкой владельца, если нужно)
    async def get_by_id(
        self, character_id: UUID
    ) -> Character:
        query = select(Character).where(Character.id == character_id)
        result = await self.session.execute(query)
        character = result.scalars().first()
        if not character:
            raise NotFoundError("Персонаж не найден")

        return character

    # 🔹 Получить всех персонажей пользователя
    async def get_by_user(self, user_id: UUID) -> List[Character]:
        query = select(Character).where(Character.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()

    # 🔹 Создать нового персонажа
    async def create_character(self, character_data: CharacterCreate) -> Character:
        new_char = Character(**character_data.model_dump())
        self.session.add(new_char)
        await self.session.commit()
        await self.session.refresh(new_char)
        return new_char

    # 🔹 Обновить данные персонажа
    async def update_character(
        self, character_id: UUID, data: CharacterUpdate,
    ) -> Character:
        character = await self.get_by_id(character_id)
        updated_data = data.model_dump(exclude_unset=True)
        for field, value in updated_data.items():
            if hasattr(character, field):
                setattr(character, field, value)

        self.session.add(character)
        await self.session.commit()
        await self.session.refresh(character)
        return character

    # 🔹 Удалить персонажа
    async def delete_character(self, character_id: UUID) -> None:
        character = await self.get_by_id(character_id)
        await self.session.delete(character)
        await self.session.commit()
