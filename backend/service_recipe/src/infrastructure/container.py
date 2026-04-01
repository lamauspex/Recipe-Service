"""
DI контейнер для управления зависимостями user_service
Использует dependency-injector для инверсии управления

ВАЖНО: Контейнер НЕ управляет репозиториями и бизнес-сервисами!
Репозитории и сервисы создаются через FastAPI Dependencies в dependencies.py

Контейнер управляет только:
- Конфигурациями
- Stateless сервисами (PasswordService, JWTService)
- Ресурсами
"""

from dependency_injector import containers, providers

from backend.service_recipe.src.config import (
    ApiRConfig,
    UserServiceConfig,
    RebbitConfig
)
from backend.shared.database import (
    DataBaseConfig,
    ConnectionManager,
    SessionManager
)


class Container(containers.DeclarativeContainer):
    """
    Главный контейнер зависимостей recipe_service

    Управляет конфигурацией и stateless сервисами.

    Принципы:
    - Контейнер независим от других сервисов
    - Репозитории получают сессию через FastAPI Depends
    - Stateless сервисы создаются через Singleton
    """

    # ==========================================
    # КОНФИГУРАЦИЯ (через DI)
    # ==========================================
    # Создаем экземпляры конфигураций через Factory
    # Factory создает новый экземпляр каждый раз при запросе
    api_config = providers.Factory(ApiRConfig)
    user_config = providers.Factory(UserServiceConfig)
    db_config = providers.Factory(DataBaseConfig)
    rebbit_config = providers.Factory(RebbitConfig)

    # ==========================================
    # Сессия
    # ==========================================
    # Один engine на всё приложение
    connection_manager = providers.Singleton(
        ConnectionManager,
        database_config=db_config
    )

    # Сессии создаются из engine
    session_manager = providers.Factory(
        SessionManager,
        engine=connection_manager.provided.engine
    )

    # ==========================================
    # АГРЕГАТОРЫ
    # ==========================================
    # Все конфигурации в одном объекте
    configs = providers.Factory(
        lambda api, user, rebbit, db: type('Configs', (), {
            'api': api,
            'user': user,
            'db': db,
            'rebbit': rebbit
        })(),
        api=api_config,
        user=user_config,
        db=db_config,
        rebbit=rebbit_config
    )


# Создаем глобальный экземпляр контейнера
container = Container()

# Инициализируем ресурсы (если добавлю их в будущем)
container.init_resources()
