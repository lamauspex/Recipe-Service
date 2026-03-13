"""
Главный файл запуска всех сервисов
"""

import logging

import uvicorn

from backend.service_user import app_users


# Отключаем ВСЕ логи Uvicorn ДО запуска
for logger_name in [
    "uvicorn",
    "uvicorn.access",
    "uvicorn.error",
    "uvicorn.asgi"
]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)


if __name__ == "__main__":
    uvicorn.run(
        app_users,
        log_level="warning",
        access_log=False
    )
