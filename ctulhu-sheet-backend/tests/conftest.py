import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import get_async_session

# ==========================================================
# ⚙️ Настраиваем временную тестовую базу данных (SQLite in-memory)
# ==========================================================
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


# ==========================================================
# 📦 Переопределяем зависимость get_async_session
# ==========================================================
async def override_get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


# ==========================================================
# 🧪 Pytest фикстуры
# ==========================================================
@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Используем один event loop для всех тестов."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Создаём все таблицы перед тестами."""
    async with engine_test.begin() as conn:
        from app.models import User, Character  # важно: импорт, чтобы таблицы зарегистрировались
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # async with engine_test.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Асинхронный HTTP клиент для тестов."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac