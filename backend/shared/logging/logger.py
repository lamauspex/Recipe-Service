"""
Базовый логгер с поддержкой контекста
"""

from typing import Any, Optional
from functools import lru_cache

import structlog
from structlog.typing import EventDict


# Тип для логгера
Logger = structlog.stdlib.BoundLogger


class ContextLogger:
    """
    Логгер с автоматическим контекстом

    Позволяет добавить общие поля (layer, service_name и т.д.)
    которые будут добавлены к каждому сообщению.
    """

    def __init__(
        self,
        logger: Logger,
        **context
    ):
        self._logger = logger
        self._context = context

    def bind(self, **kwargs) -> "ContextLogger":
        """Добавляет новые поля к контексту"""
        new_context = {**self._context, **kwargs}
        return ContextLogger(self._logger, **new_context)

    def _add_context(self, event_dict: EventDict) -> EventDict:
        """Добавляет контекст к каждому логу"""
        for key, value in self._context.items():
            if key not in event_dict:
                event_dict[key] = value
        return event_dict

    def debug(self, event: str, **kwargs: Any) -> None:
        self._logger.debug(event, **kwargs)

    def info(self, event: str, **kwargs: Any) -> None:
        self._logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        self._logger.warning(event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        self._logger.error(event, **kwargs)

    def exception(self, event: str, **kwargs: Any) -> None:
        """Логирование исключения с трассировкой стека"""
        self._logger.exception(event, **kwargs)

    def critical(self, event: str, **kwargs: Any) -> None:
        self._logger.critical(event, **kwargs)

    def log(self, level: str, event: str, **kwargs: Any) -> None:
        """Универсальный метод логирования"""
        getattr(self._logger, level)(event, **kwargs)


@lru_cache(maxsize=1)
def get_logger(name: Optional[str] = None) -> ContextLogger:
    """
    Возвращает настроенный логгер

    Args:
        name: Имя логгера (обычно __name__)

    Returns:
        ContextLogger с настроенным процессором
    """
    logger = structlog.get_logger(name)

    # Добавляем процессор для контекста
    logger = logger.bind()

    return ContextLogger(logger=logger)
