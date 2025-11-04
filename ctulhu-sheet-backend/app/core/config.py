from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
   # --- Основные настройки ---
    PROJECT_NAME: str = "Call of Cthulhu Sheet API"
    DEBUG: bool = True
    UVICORN_LOG_LEVEL: str = "warning"
    APP_LOG_LEVEL: str = "DEBUG"
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 3000

    # --- Настройки БД ---
    DATABASE_URL: SecretStr = SecretStr("sqlite+aiosqlite:///./cthulhu.db")

    # --- JWT ---
    JWT_SECRET_KEY: SecretStr = SecretStr("super_secret_key")
    JWT_ALGORITHM: str = "HS256"

    # --- Время жизни токенов (в секундах) ---
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 15 * 60        # 15 минут
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 3 * 24 * 3600 # 3 дня

    


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()