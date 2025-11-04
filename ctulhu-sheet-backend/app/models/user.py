"""
Модуль модели пользователя.

Определяет структуру таблицы пользователей в базе данных
и базовые модели для создания и чтения данных пользователя.
"""

from typing import List, TYPE_CHECKING
from datetime import datetime
from pydantic import EmailStr
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from uuid import uuid4




class UserBase(SQLModel):
    """
    Базовая модель пользователя (без приватных данных).
    Используется для общих полей, доступных вне БД.
    """

    email: EmailStr = Field(index=True, unique=True, description="Email пользователя")


class User(UserBase, table=True):
    """
    Основная таблица пользователей.
    Хранит аутентификационные данные и активные токены.
    """

    id: Optional[UUID] = Field(primary_key=True, default_factory=uuid4)
    hashed_password: str = Field(description="Хэш пароля пользователя")
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Дата и время регистрации пользователя"
    )
    admin: bool = Field(description="Права администратора", default=False)

    access_token: Optional[str] = Field(default=None, description="Текущий access-токен JWT")
    refresh_token: Optional[str] = Field(default=None, description="Текущий refresh-токен JWT")


class UserCreate(UserBase):
    """
    Модель для создания нового пользователя.
    Используется при регистрации.
    """

    password: str = Field(min_length=6, description="Пароль пользователя")


class UserRead(UserBase):
    """
    Модель для возврата данных пользователя в API.
    Без пароля и токенов.
    """

    id: UUID
    created_at: datetime = Field(
        description="Дата и время регистрации пользователя"
    )
    admin: bool  = Field(description="Права администратора", default=False)


class TokenPair(SQLModel):
    """
    Модель для возврата пары токенов пользователю.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"