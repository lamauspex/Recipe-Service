"""
Service orchestrator - запускает FastAPI сервис

Принципы:
- Единая точка входа для запуска
- Инициализация всех зависимостей
- Graceful shutdown через FastAPI lifespan
"""

import uvicorn

from backend.service_recipe.src.application import create_app
from backend.service_recipe.src.infrastructure import container


def run_service():
    """
    Запускает FastAPI сервис

    Читает конфигурацию из DI контейнера и запускает uvicorn.
    """
    api_config = container.api_config()

    uvicorn.run(
        app=create_app(),
        host=api_config.HOST,
        port=api_config.PORT,
        log_level="warning",
        access_log=True
    )
