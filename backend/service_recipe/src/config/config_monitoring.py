"""  Конфигурация мониторинга и логирования """


from pydantic import Field

from backend.service_recipe.src.config.base import BaseRConfig


class MonitoringConfig(BaseRConfig):
    """Конфигурация мониторинга и логирования"""

    # ЛОГИРОВАНИЕ
    LOG_LEVEL: str = Field(
        description="Уровень логирования"
    )
    LOG_FORMAT: str = Field(
        description="Формат логов"
    )
    HEALTH_CHECK_PATH: str = Field(
        description="Путь health check"
    )

    @property
    def DEBUG(self) -> bool:
        """Режим отладки (для совместимости)"""
        return self.LOG_LEVEL in ("DEBUG", "debug")
