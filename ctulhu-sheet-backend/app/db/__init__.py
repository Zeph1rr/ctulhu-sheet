"""
Модуль для управления подключением к базе данных.

Содержит:
- async_session_maker — фабрика асинхронных сессий SQLModel
- init_db() — инициализация базы данных (создание таблиц)

Использование:
    from app.db import async_session_maker, init_db
"""

from .session import get_async_session, init_db, async_session

__all__ = ["get_async_session", "init_db", "async_session"]