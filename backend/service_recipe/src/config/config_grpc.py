"""Конфигурация для интеграции с user_service"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class UserServiceConfig(BaseSettings):
    """Конфигурация для подключения к user_service"""

    model_config = SettingsConfigDict(
        env_file=r"backend/service_recipe/.env",
        extra='ignore',
        env_prefix="USER_SERVICE_",
        validate_assignment=True,
    )

    GRPC_HOST: str = "localhost"
    GRPC_PORT: int = 50051

    # JWT настройки
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"


def get_settings() -> UserServiceConfig:
    return UserServiceConfig()
