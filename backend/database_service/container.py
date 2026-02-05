"""
DI контейнер для управления зависимостями
Использует dependency-injector для инверсии управления
"""

from dependency_injector import containers, providers

from .database import DataBaseConfig
from .connection import DatabaseManager


class Container(containers.DeclarativeContainer):
    """
    Главный контейнер зависимостей приложения
    """

    # Конфигурация
    config = providers.Configuration()

    # Загружаем конфигурацию из .env файла
    config.from_pydantic_settings(DataBaseConfig)

    # Провайдеры базы данных
    database_config = providers.Singleton(
        DataBaseConfig,
        DB_USER=config.DB_USER,
        DB_HOST=config.DB_HOST,
        DB_PORT=config.DB_PORT,
        DB_NAME=config.DB_NAME,
        DB_PASSWORD=config.DB_PASSWORD,
        DB_DRIVER=config.DB_DRIVER,
        TESTING=config.TESTING,
        DEBUG=config.DEBUG,
    )

    database_manager = providers.Singleton(
        DatabaseManager,
    )

    # Фабрика для создания сессий БД
    db_session = providers.Factory(
        database_manager.provided.get_db_session,
    )

    # Генератор сессий для FastAPI зависимостей
    db_dependency = providers.Factory(
        database_manager.provided.get_db,
    )

    # Контекстный менеджер для сессий БД
    db_context = providers.Factory(
        database_manager.provided.get_db_context,
    )


# Создаем глобальный экземпляр контейнера
container = Container()
container.init_resources()
container.wire(packages=["."])
