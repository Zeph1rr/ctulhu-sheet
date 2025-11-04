"""
API-маршруты для аутентификации пользователей.

Реализует регистрацию, авторизацию и обновление токенов.
Вся бизнес-логика находится в сервисе AuthService.
"""
from uuid import UUID
from typing import Annotated
from pydantic import SecretStr
from fastapi import APIRouter, status, Query, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ...models.user import UserCreate, UserRead, TokenPair
from ...service import AuthService
from ...core.api import get_current_user, get_current_admin
from ...core.errors import ForbidenError

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.put("/{id}", response_model=UserRead)
async def change_password(
    id: UUID,
    new_password: SecretStr,
    current_user: UserRead = Depends(get_current_user),
    service: AuthService = Depends()
):
    if current_user.id != id and not current_user.admin:
        raise ForbidenError("Нельзя изменить пароль другого пользователя")
    return await service.change_password(id, new_password.get_secret_value())

@router.delete("/{id}", status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
async def delete_user(
    id: UUID,
    current_user: UserRead = Depends(get_current_user),
    service: AuthService = Depends()
):
    if current_user.id != id and not current_user.admin:
        raise ForbidenError("Нельзя удалить другого пользователя")
    await service.delete(id)
    return {}


@router.get("/{id}", response_model=UserRead)
async def get_user(
    id: UUID,
    current_user: UserRead = Depends(get_current_user),
    service: AuthService = Depends()
):
    return await service.get(id)

@router.get("/", response_model=list[UserRead])
async def get_all_users(
    current_user: UserRead = Depends(get_current_admin),
    service: AuthService = Depends()
):
    return await service.get_multi()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    service: AuthService = Depends(),
):
    """
    Регистрация нового пользователя.

    Принимает email и пароль, хэширует пароль и сохраняет пользователя в БД.
    """
    return await service.register_user(user_data)


@router.post("/login", response_model=TokenPair)
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthService = Depends(),
):
    """
    Авторизация пользователя по email и паролю.

    Возвращает access и refresh токены.
    """
    return await service.login_user(form_data.username, form_data.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(
    refresh_token: str = Query(..., description="Refresh-токен"),
    service: AuthService = Depends(),
):
    """
    Обновление пары токенов по refresh-токену.
    """
    return await service.refresh_tokens(refresh_token)