"""
Общая конфигурация для всех микросервисов
Поддерживает разные окружения и контейнеризацию
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class DatabaseSettings(BaseSettings):
    """Настройки базы данных"""
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # Для контейнеризации
    DB_SERVICE_NAME: Optional[str] = None

    @property
    def database_url(self) -> str:
        """Получение DSN для подключения"""
        host = self.DB_SERVICE_NAME or self.DB_HOST
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{host}:{self.DB_PORT}/{self.DB_NAME}"
        )


class AuthSettings(BaseSettings):
    """Настройки аутентификации"""
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class ServiceSettings(BaseSettings):
    """Общие настройки сервиса"""
    SERVICE_PORT: int = 8000
    SERVICE_NAME: str = "user-service"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # CORS настройки
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]


class Settings(DatabaseSettings, AuthSettings, ServiceSettings):
    """Объединенные настройки"""

    class Config:
        env_file = ".env"
        case_sensitive = False

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            # Приоритеты: переменные окружения > .env файл
            return env_settings, init_settings, file_secret_settings


@lru_cache()
def get_settings() -> Settings:
    """
    Получение настроек с кэшированием
    Обеспечивает эффективность и единообразие настроек
    """
    return Settings()


def get_service_settings(service_name: str) -> ServiceSettings:
    """
    Получение специфичных настроек для конкретного сервиса
    Может быть переопределено в каждом сервисе
    """
    settings = get_settings()
    settings.SERVICE_NAME = service_name
    return settings
