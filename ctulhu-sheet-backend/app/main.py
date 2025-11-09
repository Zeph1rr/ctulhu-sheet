from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from .api.routes import api_router
from .service.auth_service import AuthService
from .core.config import settings
from .core.logger import configure_logger
from .core.logger import loggingMiddleware
from .core.utils import get_project_data
from .core.errors import BadRequestError
from .db.session import init_db, async_session
from .models.user import UserCreate

tags_metadata = [
    {
        "name": "Auth",
        "description": "Эндпоинты для работы с учетными данными пользователей",
    },
    {
        "name": "Characters",
        "description": "Эндпоинты для работы с персонажами/листами"
    }
]

app_name, app_version = get_project_data()

async def create_superuser():
    try:
        async with async_session() as session:
            service = AuthService(session)
            user = UserCreate(email="admin@zeph1rr.ru", password="123123")
            superuser = await service.register_user(user)
            await service.update(superuser, {"admin": True})
    except BadRequestError as _ex:
        pass
        


async def lifespan(_):
    configure_logger(log_level=settings.APP_LOG_LEVEL)
    logger.info(f"Application {app_name}:{app_version} successfully started")
    logger.debug(
        f"Application started on http://{settings.SERVER_HOST}:{settings.SERVER_PORT}"
    )
    await init_db()
    await create_superuser()
    yield
    logger.info(f"Application {app_name}:{app_version} successfully stoped")


app = FastAPI(
    title=app_name,
    description="Бекенд приложения autoiinovatic",
    version=app_version,
    openapi_tags=tags_metadata,
    openapi_url="/api/v1/openapi.json" if settings.DEBUG else "",
    docs_url="/api/swagger-ui" if settings.DEBUG else "",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    raise BadRequestError(detail=str(exc)) 

app.add_middleware(BaseHTTPMiddleware, dispatch=loggingMiddleware)

app.include_router(router=api_router, prefix="/api/v1")
