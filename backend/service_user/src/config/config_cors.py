"""Конфигурация CORS"""

from pydantic import Field

from .base import BaseConfig


class CORSConfig(BaseConfig):
    """Конфигурация CORS"""

    CORS_ORIGINS: list = Field(
        default=["http://localhost:3000"],
        description="Разрешённые источники"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        description="Разрешить куки и заголовки авторизации"
    )
