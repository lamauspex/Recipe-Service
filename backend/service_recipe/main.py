"""
Главный файл запуска сервиса RECIPE_SERVICE
"""


# import logging

import uvicorn

from backend.service_recipe.src.application import create_app
from backend.service_recipe.src.infrastructure import container


# Отключаем ВСЕ логи Uvicorn ДО запуска
# for logger_name in [
#     "uvicorn",
#     "uvicorn.access",
#     "uvicorn.error",
#     "uvicorn.asgi"
# ]:
#     logging.getLogger(logger_name).setLevel(logging.WARNING)


if __name__ == "__main__":
    # Читаем настройки из контейнера
    api_config = container.api_config()

    uvicorn.run(
        app=create_app(),
        host=api_config.HOST,
        port=api_config.PORT,
        log_level="warning",
        access_log=True
    )
