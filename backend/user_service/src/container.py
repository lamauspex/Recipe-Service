"""
DI контейнер для управления зависимостями user_service
Использует dependency-injector для инверсии управления
"""

from dependency_injector import containers, providers

from backend.user_service.src.config.settings import settings
from backend.user_service.src.core.service_jwt import JWTService
from backend.user_service.src.core.service_password import PasswordService
from backend.user_service.src.service.auth_service.auth_service import AuthService
from backend.user_service.src.service.register_service.register_service import RegisterService
from backend.user_service.src.repositories.sql_user_repository import SQLUserRepository
from backend.user_service.src.repositories.sql_role_repository import SQLRoleRepository
from backend.user_service.src.repositories.sql_token_repository import SQLTokenRepository


class Container(containers.DeclarativeContainer):
    """
    Главный контейнер зависимостей user_service
    Управляет конфигурацией, репозиториями и сервисами
    """

    # ==========================================
    # КОНФИГУРАЦИЯ
    # ==========================================

    config = providers.Configuration()

    # Загружаем конфигурацию из settings синглтона
    config.auth = providers.Object(settings.auth)
    config.api = providers.Object(settings.api)
    config.cache = providers.Object(settings.cache)
    config.monitoring = providers.Object(settings.monitoring)

    # Доступ к настройкам JWT и паролей
    config.jwt_secret_key = providers.Object(settings.SECRET_KEY)
    config.jwt_algorithm = providers.Object(settings.ALGORITHM)
    config.access_token_expire_minutes = providers.Object(
        settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    config.refresh_token_expire_days = providers.Object(
        settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    # ==========================================
    # ЗАВИСИМОСТИ ОТ БАЗЫ ДАННЫХ
    # ==========================================

    # Зависимость сессии БД будет инжектироваться из FastAPI Depends
    db_dependency = providers.Dependency()

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
        secret_key=config.jwt_secret_key,
        algorithm=config.jwt_algorithm
    )

    # ==========================================
    # РЕПОЗИТОРИИ
    # ==========================================

    # Репозиторий пользователей
    user_repository = providers.Factory(
        SQLUserRepository,
        db=db_dependency
    )

    # Репозиторий ролей
    role_repository = providers.Factory(
        SQLRoleRepository,
        db=db_dependency
    )

    # Репозиторий токенов
    token_repository = providers.Factory(
        SQLTokenRepository,
        db=db_dependency
    )

    # Провайдер для получения всех репозиториев одним вызовом
    repositories = providers.Factory(
        lambda user_repo, role_repo, token_repo: (
            user_repo,
            role_repo,
            token_repo
        ),
        user_repo=user_repository,
        role_repo=role_repository,
        token_repo=token_repository
    )

    # ==========================================
    # БИЗНЕС-СЕРВИСЫ
    # ==========================================

    # Сервис аутентификации
    auth_service = providers.Factory(
        AuthService,
        user_repo=user_repository,
        password_service=password_service,
        jwt_service=jwt_service
    )

    # Сервис регистрации
    register_service = providers.Factory(
        RegisterService,
        user_repo=user_repository,
        password_service=password_service
    )

    # ==========================================
    # ФАБРИКИ (для обратной совместимости)
    # ==========================================

    # Фабрика для создания репозиториев (сохранена для совместимости)
    repository_factory = providers.Factory(
        lambda db: (
            SQLUserRepository(db),
            SQLRoleRepository(db),
            SQLTokenRepository(db)
        )
    )

    # ==========================================
    # АГРЕГАТОРЫ СЕРВИСОВ
    # ==========================================

    # Все бизнес-сервисы в одном объекте для удобства
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

# Подключаем контейнер к пакетам user_service для использования @inject и Provide
container.wire(
    packages=[
        "backend.user_service.src.api",
        "backend.user_service.src.service",
        "backend.user_service.src.factories",
    ]
)
