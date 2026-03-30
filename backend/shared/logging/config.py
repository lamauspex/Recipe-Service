"""
Конфигурация structlog для проекта
"""

import logging
import os
import sys

import structlog
from logging.handlers import RotatingFileHandler


def setup_logging(
    debug: bool = False,
    json_output: bool | str = False,
    log_file: str = "logs/app.log"
) -> None:
    """
    Настраивает structlog для всего приложения

    Args:
        debug: Включить DEBUG уровень (более подробный вывод)
        json_output: Выводить в JSON формате (для продакшена)
    """

    if isinstance(json_output, str):
        json_output = json_output.lower() == "json"

    # Настройка процессоров в зависимости от режима
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
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

    # Создание директории для логов, если её нет
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Файл - все события включая DEBUG
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10_000_000,  # 10 MB
        backupCount=5         # 5 файлов
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    # Консоль - только важные события (INFO и выше)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    # Настройка стандартного logging
    # Консоль
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # Связываем стандартный logging с файлом
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.DEBUG)

    # Настройка structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Привязываем file_handler ко всем логгерам
    # Это гарантирует, что structlog будет писать в файл
    for name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(name)
        if not logger.handlers:  # Добавляем только если нет обработчиков
            logger.addHandler(file_handler)
            logger.setLevel(logging.DEBUG)


def get_log_level(debug: bool = False) -> int:
    """Возвращает уровень логирования"""
    return logging.DEBUG if debug else logging.INFO
