"""
Главный файл приложения Database Service

Создаёт FastAPI приложение для управления базой данных.
Этот сервис может использоваться как standalone или как часть
монолитного приложения через DI контейнер.

"""

from fastapi import FastAPI

from .src.container import container
from .src.lifespan import lifespan


def create_app() -> FastAPI:
    """
    Приложение предоставляет:
    - Swagger документацию на /docs (если включено в конфиге)
    - ReDoc документацию на /redoc
    - Автоматическое управление соединениями через lifespan
    - Dependency injection для сессий БД
    """

    # Получаем настройки из DI контейнера
    config = container.config

    # Создаём FastAPI приложение
    app = FastAPI(
        title=config.API_TITLE,
        description=config.API_DESCRIPTION,
        version=config.API_VERSION,
        # Документация API (Swagger/ReDoc)
        docs_url="/docs" if config.API_DOCS_ENABLED else None,
        redoc_url="/redoc" if config.API_DOCS_ENABLED else None,
        # Lifespan для graceful shutdown соединений
        lifespan=lifespan
    )

    return app


# Приложение по умолчанию для импорта
app_database = create_app()
