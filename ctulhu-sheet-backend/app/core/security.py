"""
Модуль безопасности приложения.

Содержит функции для:
- Хэширования и проверки паролей
- Генерации и валидации JWT-токенов (access/refresh)
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Tuple

from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import settings


# --- Настройка контекста для хэширования паролей ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==============================================================
# Работа с паролями
# ==============================================================

def get_password_hash(password: str) -> str:
    """Возвращает bcrypt-хэш пароля."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля его хэшу."""
    return pwd_context.verify(plain_password, hashed_password)


# ==============================================================
# Работа с JWT-токенами
# ==============================================================

def create_token(data: dict[str, Any], expires_in_seconds: int) -> str:
    """
    Создает JWT-токен с заданным временем жизни (в секундах).

    Возвращает:
        token: str
    """
    to_encode = data.copy()
    expire_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
    to_encode.update({"exp": expire_at})

    secret = settings.JWT_SECRET_KEY.get_secret_value()
    algorithm = settings.JWT_ALGORITHM

    encoded_jwt = jwt.encode(to_encode, secret, algorithm=algorithm)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Декодирует JWT-токен и возвращает его payload.
    Выбрасывает JWTError, если токен недействителен.
    """
    secret = settings.JWT_SECRET_KEY.get_secret_value()
    algorithm = settings.JWT_ALGORITHM
    return jwt.decode(token, secret, algorithms=[algorithm])


def create_access_and_refresh_tokens(user_id: int) -> dict[str, Any]:
    """
    Создает пару (access, refresh) токенов для указанного пользователя.
    Возвращает словарь:
        {
            "access_token": str,
            "refresh_token": str
        }
    """
    access_token = create_token(
        {"sub": str(user_id), "type": "access"},
        settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )

    refresh_token = create_token(
        {"sub": str(user_id), "type": "refresh"},
        settings.REFRESH_TOKEN_EXPIRE_SECONDS,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }