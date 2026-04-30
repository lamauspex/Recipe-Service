"""Конфигурация CORS"""

from pydantic import Field

from .base import BaseRConfig


class CORSConfig(BaseRConfig):
    """Конфигурация CORS"""

    CORS_ORIGINS: list = Field(
        default=["http://localhost:8001", "http://127.0.0.1:8001"],
        description="Разрешённые источники"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Разрешить куки и заголовки авторизации"
    )
