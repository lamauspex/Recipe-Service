"""
Главный файл запуска всех сервисов
"""

import logging

import uvicorn

from backend.service_user import app_users
from backend.service_user.src.container import container


# Отключаем ВСЕ логи Uvicorn ДО запуска
for logger_name in [
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "uvicorn.asgi"
]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)


if __name__ == "__main__":
    # Читаем настройки из контейнера
    api_config = container.api_config()

    uvicorn.run(
        app_users,
        host=api_config.HOST,
        port=api_config.PORT,
        log_level="warning",
        access_log=False
    )
