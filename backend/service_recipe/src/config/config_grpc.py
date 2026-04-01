""" Конфигурация для интеграции с user_service """


from pydantic import Field

from backend.service_recipe.src.config.base import BaseRConfig


class UserServiceConfig(BaseRConfig):
    """Конфигурация для подключения к user_service"""

    # СЕРВЕР
    GRPC_HOST: str = Field(description='')
    GRPC_PORT: int = Field(description='')

    # JWT настройки
    JWT_SECRET_KEY: str = Field(description='')
    JWT_ALGORITHM: str = Field(description='')
