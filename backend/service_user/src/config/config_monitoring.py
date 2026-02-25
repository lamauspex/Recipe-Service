"""  Конфигурация мониторинга и логирования """

from typing import List
from pydantic import Field

from .base import BaseConfig


class MonitoringConfig(BaseConfig):
    """Конфигурация мониторинга и логирования"""

    # ЛОГИРОВАНИЕ
    LOG_LEVEL: str = Field(
        description="Уровень логирования"
    )
    LOG_FORMAT: str = Field(
        description="Формат логов"
    )
    STRUCTURED_LOGGING: bool = Field(
        description="Структурированное логирование"
    )
    ENABLE_REQUEST_LOGGING: bool = Field(
        description="Включить логи запросов"
    )
    ENABLE_EXCEPTION_LOGGING: bool = Field(
        description="Включить логи ошибок"
    )
    ENABLE_BUSINESS_LOGGING: bool = Field(
        description="Включить логи бизнес-логики"
    )

    # МОНИТОРИНГ
    MONITORING_ENABLED: bool = Field(
        description="Включить мониторинг"
    )
    METRICS_PORT: int = Field(
        description="Порт для метрик"
    )
    HEALTH_CHECK_PATH: str = Field(
        description="Путь health check"
    )
    PROMETHEUS_METRICS_PATH: str = Field(
        description="путь для Prometheus метрик"
    )

    # CORS НАСТРОЙКИ
    CORS_ORIGINS: List[str] = Field(
        description="URL-адреса для разрешения запросов"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        description="Разрешить запросу запрашивать ключевые данные"
    )
    CORS_MAX_AGE: int = Field(
        description="Для изменения текущего времени access-control-max-age"
    )

    @property
    def DEBUG(self) -> bool:
        """Режим отладки (для совместимости)"""
        return self.LOG_LEVEL in ("DEBUG", "debug")
