"""Конфигурация CORS"""

from pydantic import Field

from backend.service_user.src.config.base import BaseConfig


class CORSConfig(BaseConfig):
    """Конфигурация CORS"""

    CORS_ORIGINS: list = Field(
        default=["http://localhost:3000"],
        description="Разрешённые источники"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        description="Разрешить куки и заголовки авторизации"
    )
    CORS_MAX_AGE: int = Field(
        description="Время кеширования CORS (сек)"
    )
