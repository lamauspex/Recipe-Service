"""
Главный файл запуска сервиса RECIPE_SERVICE
"""


import uvicorn

from backend.service_recipe.src.application import create_app
from backend.service_recipe.src.infrastructure import container


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
