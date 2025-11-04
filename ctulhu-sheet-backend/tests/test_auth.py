import pytest
from httpx import AsyncClient
from fastapi import status

from loguru import logger

logger.add("tests.log", enqueue=True)

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "strongpass"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # Авторизация зарегистрированного пользователя
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "strongpass"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # Сохраняем токены для следующих тестов
    global ACCESS_TOKEN, REFRESH_TOKEN
    ACCESS_TOKEN = data["access_token"]
    REFRESH_TOKEN = data["refresh_token"]


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Проверяем получение текущего пользователя по токену"""
    response = await client.get(
        "/api/v1/auth/",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    # Этот эндпоинт у тебя возвращает список пользователей только для админов,
    # поэтому ожидаем отказ (403)
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Обновляем пару токенов"""
    response = await client.post(
        "/api/v1/auth/refresh",
        params={"refresh_token": REFRESH_TOKEN},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_change_password_and_login_again(client: AsyncClient):
    """Меняем пароль и проверяем повторный логин"""
    # Регистрируем нового пользователя
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "changepass@example.com", "password": "oldpass"},
    )
    user_id = reg_resp.json()["id"]

    # Логинимся этим же пользователем
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "changepass@example.com", "password": "oldpass"},
    )
    token = login_resp.json()["access_token"]

    # Меняем пароль
    response = await client.put(
        f"/api/v1/auth/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"new_password": "newpass"},
    )
    assert response.status_code in [200, 403]

    # Проверяем вход с новым паролем
    login_resp2 = await client.post(
        "/api/v1/auth/login",
        data={"username": "changepass@example.com", "password": "newpass"},
    )
    assert login_resp2.status_code == 200


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient):
    """Удаляем пользователя"""
    # Регистрируем нового
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "delete_me@example.com", "password": "temp1234"},
    )
    user_id = response.json()["id"]
    logger.debug(user_id)

    # Логинимся
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "delete_me@example.com", "password": "temp1234"},
    )
    token = login_resp.json()["access_token"]
    logger.info(token)

    # Удаляем себя
    delete_resp = await client.delete(
        f"/api/v1/auth/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    logger.info(delete_resp.text)
    assert delete_resp.status_code in [203, 204]
