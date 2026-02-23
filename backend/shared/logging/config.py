"""
Конфигурация structlog для проекта
"""

import logging
import sys

import structlog


def setup_logging(
    debug: bool = False,
    json_output: bool = False
) -> None:
    """
    Настраивает structlog для всего приложения

    Args:
        debug: Включить DEBUG уровень (более подробный вывод)
        json_output: Выводить в JSON формате (для продакшена)
    """

    # Настройка процессоров в зависимости от режима
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_output:

        # JSON формат для продакшена (логирование в файлы, ELK и т.д.)
        processors.append(structlog.processors.JSONRenderer())

    else:

        # Красивый текстовый формат для консоли
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True
            )
        )

    # Настройка structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Настройка стандартного logging для совместимости
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if debug else logging.INFO,
    )


def get_log_level(debug: bool = False) -> int:
    """Возвращает уровень логирования"""
    return logging.DEBUG if debug else logging.INFO
