"""
DI контейнер для управления зависимостями user_service
Использует dependency-injector для инверсии управления
"""

from dependency_injector import containers, providers

from backend.database_service import db_dependency
from backend.user_service.src.config import (
    ApiConfig,
    AuthConfig,
    CacheConfig,
    MonitoringConfig
)
from backend.user_service.src.core import (
    JWTService,
    PasswordService
)
from backend.user_service.src.service import (
    AuthService,
    RegisterService
)
from backend.user_service.src.repositories import (
    SQLUserRepository,
    SQLTokenRepository
)


class Container(containers.DeclarativeContainer):
    """
    Главный контейнер зависимостей user_service
    Управляет конфигурацией, репозиториями и сервисами
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
    # ЗАВИСИМОСТИ ОТ БАЗЫ ДАННЫХ
    # ==========================================

    # Зависимость сессии БД будет инжектироваться из FastAPI Depends
    db_dependency = providers.Factory(db_dependency)

    # ==========================================
    # CORE СЕРВИСЫ
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

    # ==========================================
    # РЕПОЗИТОРИИ
    # ==========================================

    # Репозиторий пользователей
    user_repository = providers.Factory(
        SQLUserRepository,
        db=db_dependency
    )

    # Репозиторий токенов
    token_repository = providers.Factory(
        SQLTokenRepository,
        db=db_dependency
    )

    # ==========================================
    # БИЗНЕС-СЕРВИСЫ
    # ==========================================

    # Сервис аутентификации
    auth_service = providers.Factory(
        AuthService,
        user_repo=user_repository,
        password_service=password_service,
        jwt_service=jwt_service,
        auth_config=auth_config,
        api_config=api_config,
    )

    # Сервис регистрации
    register_service = providers.Factory(
        RegisterService,
        user_repo=user_repository,
        password_service=password_service,
        auth_config=auth_config,
    )

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

    # Все бизнес-сервисы в одном объекте
    services = providers.Factory(
        lambda auth, register: type('Services', (), {
            'auth': auth,
            'register': register
        })(),
        auth=auth_service,
        register=register_service
    )


# Создаем глобальный экземпляр контейнера
container = Container()

# Инициализируем ресурсы (если они будут добавлены в будущем)
container.init_resources()

# Подключаем контейнер к пакетам user_service
# для использования @inject и Provide
container.wire(
    packages=[
        "backend.user_service.src.api",
        "backend.user_service.src.service",
    ]
)
