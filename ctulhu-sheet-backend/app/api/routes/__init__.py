"""
Пакет маршрутов API.

Содержит все основные роутеры приложения (эндпоинты FastAPI).
Каждый роутер отвечает за отдельную функциональность.

Список доступных роутеров:
- auth: регистрация, вход и обновление токенов
"""

from fastapi import APIRouter
from fastapi import Depends
from .auth import router as auth_router
from .character import router as character_router
from ...models.user import UserRead
from ...core.errors import ErrorResponseModel
from ...core.errors import ValidationErrorModel
from ...core.api import get_current_user
from ...core.config import settings



# --- Главный роутер приложения ---
api_router = APIRouter(responses={
        400: {"model": ErrorResponseModel},
        401: {"model": ErrorResponseModel},
        403: {"model": ErrorResponseModel},
        404: {"model": ErrorResponseModel},
        422: {"model": ValidationErrorModel},
        500: {"model": ErrorResponseModel},
    }
)

# Подключаем роутеры
api_router.include_router(auth_router)
api_router.include_router(character_router)

if settings.DEBUG:

    @api_router.get("/")
    async def hello():
        return {"status": "ok"}

    @api_router.get("/secured")
    async def hello_secured(
        current_user: UserRead = Depends(get_current_user)
    ):
        return {
            "status": "ok",
            "user": current_user.model_dump()
        }



__all__ = ["api_router"]