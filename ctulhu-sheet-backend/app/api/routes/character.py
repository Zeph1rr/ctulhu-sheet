"""
API-маршруты для управления персонажами (Character).

Реализует создание персонажа и получение персонажа по ID.
Ограничено авторизацией через JWT.
"""

from uuid import UUID
from fastapi import APIRouter, status, Depends

from ...models.character import Character, CharacterCreate, CharacterUpdate
from ...models.user import UserRead
from ...service.character_service import CharacterService
from ...core.api import get_current_user
from ...core.errors import ForbidenError

router = APIRouter(prefix="/characters", tags=["Characters"])


@router.post(
    "/",
    response_model=Character,
    status_code=status.HTTP_201_CREATED,
)
async def create_character(
    character_data: CharacterCreate,
    current_user: UserRead = Depends(get_current_user),
    service: CharacterService = Depends(),
):
    """
    Создать нового персонажа, принадлежащего текущему пользователю.
    """
    # 🚫 Безопасность — запрещаем создание от имени другого пользователя
    if character_data.user_id != current_user.id:
        if not current_user.admin:
            character_data.user_id = current_user.id
        #raise ForbidenError("Нельзя создавать персонажей от имени другого пользователя")

    return await service.create_character(character_data)


@router.get(
    "/{character_id}",
    response_model=Character,
    status_code=status.HTTP_200_OK,
)
async def get_character(
    character_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    service: CharacterService = Depends(),
):
    """
    Получить данные персонажа по его ID.
    Доступ разрешён только владельцу персонажа.
    """
    character = await service.get_by_id(character_id)
    if character.user_id != current_user.id and not current_user.admin:
        raise ForbidenError("Нельзя получить чужого персонажа!")
    return character

@router.get(
    "/by-user/{user_id}",
    response_model=list[Character],
    status_code=status.HTTP_200_OK,
)
async def get_my_characters(
    user_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    service: CharacterService = Depends(),
):
    """
    Получить список всех персонажей, принадлежащих текущему пользователю.
    """
    if not current_user.admin and current_user.id != user_id:
        raise ForbidenError("Нельзя получить список персонажей другого пользователя")
    return await service.get_by_user(user_id)

@router.put(
    "/{character_id}",
    response_model=Character,
    status_code=status.HTTP_200_OK,
)
async def update_character(
    character_id: UUID,
    character_data: CharacterUpdate,
    current_user: UserRead = Depends(get_current_user),
    service: CharacterService = Depends(),
):
    """
    Частично обновить данные персонажа (только если персонаж принадлежит пользователю).
    """
    character = await service.get_by_id(character_id)
    if not current_user.admin and character.user_id != current_user.id:
        raise ForbidenError("Нельзя изменить персонажа другого пользователя")
    return await service.update_character(character_id, character_data, current_user.id)

@router.delete(
    "/{character_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_character(
    character_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    service: CharacterService = Depends(),
):
    """
    Удалить персонажа (доступно только владельцу).
    """
    character = await service.get_by_id(character_id)
    if not current_user.admin and character.user_id != current_user.id:
        raise ForbidenError("Нельзя удалить персонажа другого пользователя")
    await service.delete_character(character_id, current_user.id)
    return None
