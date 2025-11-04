"""
Пакет моделей приложения.

Содержит определения ORM-моделей SQLModel, которые описывают
структуру таблиц в базе данных.

Импортируя этот пакет, ты можешь подключить все модели сразу.
"""

from .user import User, UserCreate, UserRead, TokenPair
from .character import Character, CharacterCreate, Skill, Characteristics, Weapon, Resources

__all__ = [
    "User",
    "UserCreate",
    "UserRead",
    "TokenPair",
    "Character",
    "CharacterCreate",
    "Skill",
    "Characteristics",
    "Weapon",
    "Resources"
]