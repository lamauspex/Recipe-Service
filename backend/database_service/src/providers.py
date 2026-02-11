"""
Провайдеры зависимостей для быстрого доступа к сервисам
Обеспечивают удобный интерфейс для использования в коде
"""

from typing import Generator
from sqlalchemy.orm import Session
from dependency_injector.wiring import Provide, inject

from .container import Container
from .config import DataBaseConfig


class DatabaseProviders:
    """
    Класс-провайдер для удобного доступа к зависимостям БД
    """

    @staticmethod
    @inject
    def get_db_session(
        database_manager=Provide[Container.database_manager]
    ) -> Session:
        """
        Получить сессию базы данных
        """
        return database_manager.get_db_session()

    @staticmethod
    @inject
    def get_db_context(
        database_manager=Provide[Container.database_manager]
    ) -> Generator[Session, None, None]:
        """
        Получить контекстный менеджер для сессии БД
        """
        with database_manager.get_db_context() as db:
            yield db

    @staticmethod
    @inject
    def get_db_dependency(
        database_manager=Provide[Container.database_manager]
    ) -> Generator[Session, None, None]:
        """
        Получить зависимость БД для FastAPI эндпоинтов
        """
        return database_manager.get_db()

    @staticmethod
    @inject
    def get_database_config(
        database_config=Provide[Container.database_config]
    ) -> 'DataBaseConfig':
        """
        Получить конфигурацию базы данных
        """
        return database_config


# Создаем экземпляр для удобного импорта
database_providers = DatabaseProviders()

# Экспортируем основные функции для прямого использования
get_db_session = database_providers.get_db_session
get_db_context = database_providers.get_db_context
get_db_dependency = database_providers.get_db_dependency
get_database_config = database_providers.get_database_config
