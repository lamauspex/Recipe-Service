""" Конфигурация Redis """


from pydantic import Field

from .base import BaseConfig


class CacheConfig(BaseConfig):
    """Конфигурация кэширования (Redis)"""

    REDIS_HOST: str = Field(description="Хост Redis")
    REDIS_PORT: int = Field(description="Порт Redis")
    REDIS_DB: int = Field(description="Номер базы Redis")
    REDIS_PASSWORD: str = Field(description="Пароль Redis")
    CACHE_TTL: int = Field(description="Время жизни кэша в секундах")
    CACHE_ENABLED: bool = Field(description="Включить кэширование")


cache_config = CacheConfig()
