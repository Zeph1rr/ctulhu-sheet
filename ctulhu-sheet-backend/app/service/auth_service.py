"""
Сервис для аутентификации пользователей.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..core.errors import BadRequestError, NotAutorizedError, NotFoundError


from ..models.user import User, UserCreate
from ..core.security import (
    get_password_hash,
    verify_password,
    create_access_and_refresh_tokens,
    decode_token,
)
from ..db import get_async_session
from ..service.base import BaseService


class AuthService(BaseService[User, UserCreate]):
    """Сервис управления пользователями и токенами."""

    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        # Передаём модель и сессию в базовый класс
        super().__init__(User, session)

    async def get(self, obj_id: UUID) -> Optional[User]:
        if type(obj_id) is not UUID:
            obj_id = UUID(obj_id)
        query = select(User).where(User.id == obj_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def register_user(self, user_data: UserCreate) -> User:
        query = select(User).where(User.email == user_data.email)
        result = await self.session.execute(query)
        user = result.scalars().first()
        if user:
            raise BadRequestError(
                detail="Пользователь с таким email уже существует",
            )

        hashed_password = get_password_hash(user_data.password)
        user = User(email=user_data.email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.commit()
        #await self.session.refresh(user)
        return user

    async def login_user(self, email: str, password: str) -> dict:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user or not verify_password(password, user.hashed_password):
            raise NotAutorizedError(detail="Неверный email или пароль")

        tokens = create_access_and_refresh_tokens(user.id)
        user.access_token = tokens["access_token"]
        user.refresh_token = tokens["refresh_token"]

        await self.session.commit()
        return {
            "access_token": user.access_token,
            "refresh_token": user.refresh_token,
            "token_type": "bearer",
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
            user_id = UUID(payload.get("sub"))
        except Exception:
            raise NotAutorizedError(detail="Невалидный refresh-токен")

        user = await self.get(user_id)
        if not user or user.refresh_token != refresh_token:
            raise NotAutorizedError(detail="Refresh-токен недействителен")

        tokens = create_access_and_refresh_tokens(user.id)
        user.access_token = tokens["access_token"]
        user.refresh_token = tokens["refresh_token"]

        await self.session.commit()
        return {
            "access_token": user.access_token,
            "refresh_token": user.refresh_token,
            "token_type": "bearer",
        }
    
    async def change_password(self, id: UUID, new_password: str):
        user = await self.get(id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        if verify_password(new_password, user.hashed_password):
            raise BadRequestError("Пароли должны отличаться")
        hashed_password = get_password_hash(new_password)
        
        return await self.update(
            user, 
            {
                "hashed_password": hashed_password,
                "refresh_token": None, 
                "access_token": None
            }
        )