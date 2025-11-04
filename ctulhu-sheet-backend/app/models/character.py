"""
Модуль модели персонажа (Character) для Call of Cthulhu 7e.

Содержит ORM-модель таблицы characters и связанные Pydantic-модели.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from pydantic import BaseModel, Field as PydField

# ==========================================================
# 🔹 Вложенные модели JSON-полей
# ==========================================================

class Characteristics(BaseModel):
    """Основные характеристики персонажа."""
    STR: int
    DEX: int
    INT: int
    CON: int
    APP: int
    POW: int
    SIZ: int
    EDU: int
    MOV: int


class Resources(BaseModel):
    """Производные параметры и ресурсы персонажа."""
    HP: int
    MP: int
    SAN: int
    LUCK: int
    Build: int = 0
    DamageBonus: str = "0"
    Move: int = 8


class Skill(BaseModel):
    """Навык персонажа."""
    name: str
    value: int


class Weapon(BaseModel):
    """Оружие персонажа."""
    name: str
    skill: str
    damage: str
    range: Optional[str] = None
    attacks: Optional[int] = 1
    ammo: Optional[int] = None
    malfunction: Optional[str] = None


class Combat(BaseModel):
    """Боевые параметры персонажа."""
    dodge: int
    build: int = 0
    damage_bonus: str = "0"
    move: int = 8
    weapons: List[Weapon] = []


class Backstory(BaseModel):
    """История персонажа."""
    personal_description: Optional[str] = None
    ideology_beliefs: Optional[str] = None
    significant_people: Optional[str] = None
    meaningful_locations: Optional[str] = None
    treasured_possessions: Optional[str] = None
    traits: Optional[str] = None
    injuries_scars: Optional[str] = None
    phobias_manias: Optional[str] = None
    arcane_tomes_spells: Optional[str] = None
    encounters_with_strange_entities: Optional[str] = None
    my_story: Optional[str] = None


# ==========================================================
# 🔹 ORM-модель Character
# ==========================================================

class CharacterBase(SQLModel):
    """Базовая модель персонажа, общие поля."""

    name: str = Field(description="Имя персонажа")
    occupation: Optional[str] = Field(default=None, description="Профессия персонажа")
    age: Optional[int] = Field(default=None, description="Возраст персонажа")
    gender: Optional[str] = Field(default=None, description="Пол персонажа")
    era: str = Field(default="1920s", description="Эпоха (1920s, Modern и т.д.)")

    characteristics: Characteristics = Field(sa_column=Column(JSON))
    resources: Resources = Field(sa_column=Column(JSON))
    skills: List[Skill] = Field(default_factory=list, sa_column=Column(JSON))
    combat: Optional[Combat] = Field(default=None, sa_column=Column(JSON))
    backstory: Optional[Backstory] = Field(default=None, sa_column=Column(JSON))


class Character(CharacterBase, table=True):
    """Таблица персонажей."""

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True)

    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)


# ==========================================================
# 🔹 Pydantic модели для API
# ==========================================================

class CharacterCreate(CharacterBase):
    """Модель для создания нового персонажа."""
    user_id: Optional[UUID] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Edward Derby",
                "occupation": "Writer",
                "age": 34,
                "gender": "Male",
                "era": "1920s",
                "characteristics": {
                    "STR": 60, "DEX": 50, "INT": 70, "CON": 65,
                    "APP": 55, "POW": 60, "SIZ": 75, "EDU": 80, "MOV": 8
                },
                "resources": {"HP": 14, "MP": 12, "SAN": 60, "LUCK": 45},
                "skills": [{"name": "Spot Hidden", "value": 50}],
                "combat": {"dodge": 40, "weapons": []},
                "backstory": {"personal_description": "Curious academic"},
            }
        }


class CharacterUpdate(SQLModel):
    name: Optional[str] = None
    occupation: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    era: Optional[str] = None
    characteristics: Optional[Characteristics] = None
    resources: Optional[Resources] = None
    skills: Optional[List[Skill]] = None
    combat: Optional[Combat] = None
    backstory: Optional[Backstory] = None