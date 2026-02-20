"""
DI контейнер для database_service
Единая точка входа для получения всех зависимостей
"""


from pathlib import Path

from dependency_injector import containers, providers

from .config import DataBaseConfig
from .connection import ConnectionManager, SessionManager
from .migration_runner import MigrationRunner


class Container(containers.DeclarativeContainer):
    """
    DI контейнер для database_service

    Принципы:
    - Single Responsibility: каждый провайдер делает одно
    - Dependency Inversion: зависимости через абстракции
    - Reusability: можно использовать в других сервисах
    """

    # ==================== КОНФИГУРАЦИЯ ====================

    config = providers.Singleton(DataBaseConfig)

    # ==================== СОЕДИНЕНИЯ ====================

    # Менеджер соединений (engine)
    connection_manager = providers.Singleton(
        ConnectionManager,
        database_config=config
    )

    # ==================== СЕССИИ ====================

    # Менеджер сессий (использует engine из connection_manager)
    session_manager = providers.Singleton(
        SessionManager,
        engine=connection_manager.provided.engine
    )

    # ==================== МИГРАЦИИ ====================

    migration_runner = providers.Factory(
        MigrationRunner,
        database_url=config().get_database_url,  # ✅ Без скобок!
        migrations_path=providers.Factory(
            lambda: str(Path(__file__).parent.parent / "migrations")
        )
    )

    # ==================== FASTAPI DEPENDENCIES ====================

    # FastAPI dependency для получения сессии
    db_dependency = providers.Factory(
        session_manager.provided.get_db
    )

    # ==================== УТИЛИТЫ ====================

    # Проверка подключения
    test_connection = providers.Factory(
        connection_manager.provided.test_connection
    )


# ==================== ГЛОБАЛЬНЫЙ ИНСТАНС ====================

container = Container()  # ✅ ВНЕ класса Container


# ==================== УДОБНЫЕ ИМПОРТЫ ====================

def get_container() -> Container:
    """
    Получить глобальный контейнер

    Returns:
        Экземпляр Container
    """
    return container


def get_db_dependency():
    """
    Получить FastAPI dependency для сессии БД

    Returns:
        Dependency для FastAPI

    Usage:
        from backend.database_service.src import db_dependency

        @app.get("/users")
        def get_users(db: Session = Depends(db_dependency)):
            return db.query(User).all()
    """
    return container.db_dependency


# ==================== ПРЯМОЙ ДОСТУП К МЕНЕДЖЕРАМ ====================

def get_connection_manager() -> ConnectionManager:
    """
    Получить ConnectionManager

    Returns:
        Экземпляр ConnectionManager
    """
    return container.connection_manager()


def get_session_manager() -> SessionManager:
    """
    Получить SessionManager

    Returns:
        Экземпляр SessionManager
    """
    return container.session_manager()


def get_migration_runner() -> MigrationRunner:
    """
    Получить MigrationRunner

    Returns:
        Экземпляр MigrationRunner
    """
    return container.migration_runner()
