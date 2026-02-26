"""
DI контейнер для управления зависимостями user_service
Использует dependency-injector для инверсии управления

ВАЖНО: Контейнер НЕ управляет репозиториями и бизнес-сервисами!
Репозитории и сервисы создаются через FastAPI Dependencies в dependencies.py

Контейнер управляет только:
- Конфигурациями
- Stateless сервисами (PasswordService, JWTService)
- Ресурсами (если будут добавлены)
"""

from dependency_injector import containers, providers

from backend.service_user.src.config import (
    ApiConfig,
    AuthConfig,
    CacheConfig,
    MonitoringConfig
)
from backend.service_user.src.core import (
    JWTService,
    PasswordService,
    AuthValidator
)
from backend.service_user.src.service.auth_service import AuthMapper


class Container(containers.DeclarativeContainer):
    """
    Главный контейнер зависимостей user_service

    Управляет конфигурацией и stateless сервисами.
    Репозитории и бизнес-сервисы создаются через FastAPI Dependencies
    в файле dependencies.py для корректной работы с сессиями БД.

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
    api_config = providers.Factory(ApiConfig)
    auth_config = providers.Factory(AuthConfig)
    cache_config = providers.Factory(CacheConfig)
    monitoring_config = providers.Factory(MonitoringConfig)

    # ==========================================
    # STATELESS CORE СЕРВИСЫ
    # ==========================================

    # Сервис для работы с паролями (без состояния)
    password_service = providers.Singleton(
        PasswordService
    )

    # Сервис для работы с JWT токенами (без состояния)
    jwt_service = providers.Singleton(
        JWTService,
        secret_key=auth_config.provided.SECRET_KEY,
        algorithm=auth_config.provided.ALGORITHM,
        access_token_expire_minutes=auth_config.provided.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=auth_config.provided.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    # Валидатор аутентификации
    auth_validator = providers.Singleton(AuthValidator)

    # Маппер для аутентификации
    auth_mapper = providers.Singleton(AuthMapper)

    # ==========================================
    # АГРЕГАТОРЫ (для удобства)
    # ==========================================

    # Все конфигурации в одном объекте
    configs = providers.Factory(
        lambda api, auth, cache, monitoring: type('Configs', (), {
            'api': api,
            'auth': auth,
            'cache': cache,
            'monitoring': monitoring,
        })(),
        api=api_config,
        auth=auth_config,
        cache=cache_config,
        monitoring=monitoring_config,
    )


# Создаем глобальный экземпляр контейнера
container = Container()

# Инициализируем ресурсы (если они будут добавлены в будущем)
container.init_resources()

# Подключаем контейнер к пакетам user_service
# для использования @inject и Provide
# container.wire(
#     packages=[
#         "backend.user_service.src.dependencies",
#         "backend.user_service.src.api",
#         "backend.user_service.src.service",
#     ]
# )
