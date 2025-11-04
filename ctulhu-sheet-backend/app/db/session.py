"""
Модуль для инициализации и предоставления асинхронной сессии SQLModel.
"""

from typing import AsyncGenerator

from sqlmodel import SQLModel, insert
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from ..core.config import settings


# --- Создаем асинхронный движок SQLAlchemy ---
engine = create_async_engine(
    settings.DATABASE_URL.get_secret_value(),
    echo=settings.DEBUG,
    future=True,
)


# --- Создаем фабрику асинхронных сессий ---
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# --- Инициализация базы данных ---
async def init_db() -> None:
    """Создает таблицы в базе данных, если их нет."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения асинхронной сессии."""
    async with async_session() as session:
        yield session