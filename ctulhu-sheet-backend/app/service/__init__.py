"""
Пакет `app.service` содержит бизнес-логику приложения:
CRUD-сервисы и специализированные классы для работы с моделями и БД.

Основная идея — отделить бизнес-логику от маршрутов (API) и баз данных.
Все сервисы используют асинхронную сессию SQLAlchemy через dependency injection (Depends).

Примеры:
    from app.service import AuthService

    service = AuthService()  # автоматически получает async session через Depends()
"""

from .base import BaseService
from .auth_service import AuthService

__all__ = [
    "BaseService",
    "AuthService",
]