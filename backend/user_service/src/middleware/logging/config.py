""" Конфигурация, описывающая логирование """


from __future__ import annotations
import logging
from typing import Any, Optional
import structlog

from backend.user_service.src.config.monitoring import MonitoringConfig
from backend.user_service.src.middleware.logging.utils_trace_id import trace_id_var


def get_log_level_from_config(log_level: str) -> int:
    """Преобразование строки уровня логирования в числовое значение"""
    levels = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }
    return levels.get(log_level.upper(), 20)


def setup_logging(config: Optional[MonitoringConfig] = None) -> None:
    """
    Настройка структурированного логирования на основе конфигурации

    Конфигурирует structlog для всего приложения.
    Вызывается один раз при старте приложения.

    Args:
        config: Конфигурация мониторинга
        (используется из settings если не передана)
    """
    from backend.user_service.src.config import settings

    if config is None:
        config = settings.monitoring

    # Выбор рендерера на основе конфигурации
    renderer = (
        structlog.processors.JSONRenderer()
        if config.STRUCTURED_LOGGING
        else structlog.dev.ConsoleRenderer()
    )

    # Определение уровня логирования
    log_level = get_log_level_from_config(config.LOG_LEVEL)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            filter_context,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
        context_class=dict,
    )


def filter_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Фильтрует None значения и добавляет trace_id"""
    # Фильтруем None значения
    filtered = {k: v for k, v in event_dict.items() if v is not None}

    # Добавляем trace_id если есть в контексте
    current_trace_id = trace_id_var.get()
    if current_trace_id and "trace_id" not in filtered:
        filtered["trace_id"] = current_trace_id

    return filtered
