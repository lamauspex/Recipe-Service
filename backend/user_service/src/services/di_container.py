"""
Современный DI контейнер с использованием dependency-injector
"""
from dependency_injector import containers, providers

from .infrastructure import (
    SecurityServiceAdapter,
    AuthService,
    UserRepositoryAdapter,
    TokenRepositoryAdapter
)


from ..usecases.auth.login import LoginUsecase
from ..usecases.auth.register import RegisterUsecase
from ..usecases.auth.refresh_token import RefreshTokenUsecase
from ..usecases.auth.logout import LogoutUsecase


class DIContainer(containers.DeclarativeContainer):
    """Современный DI контейнер для сервисов"""

    # Настройки
    config = providers.Configuration()

    # База данных
    db_session = providers.Singleton(
        # Здесь будет реальная сессия базы данных
        # DatabaseSession,
        # connection_string=config.database.connection_string
    )

    # Настройки безопасности
    jwt_secret = providers.Singleton(
        lambda: "your-super-secret-jwt-key-here"  # Из конфигурации
    )

    # Репозитории
    user_repository = providers.Factory(
        UserRepositoryAdapter,
        db_session=db_session
    )

    token_repository = providers.Factory(
        TokenRepositoryAdapter,
        db_session=db_session
    )

    # Сервисы безопасности
    security_service = providers.Factory(
        SecurityServiceAdapter,
        jwt_secret=jwt_secret
    )

    # Usecases
    login_usecase = providers.Factory(
        LoginUsecase,
        user_repository=user_repository,
        security_service=security_service,
        token_repository=token_repository
    )

    register_usecase = providers.Factory(
        RegisterUsecase,
        user_repository=user_repository,
        security_service=security_service
    )

    refresh_token_usecase = providers.Factory(
        RefreshTokenUsecase,
        token_repository=token_repository,
        security_service=security_service,
        user_repository=user_repository
    )

    logout_usecase = providers.Factory(
        LogoutUsecase,
        token_repository=token_repository,
        security_service=security_service
    )

    password_reset_usecase = providers.Factory(
        # PasswordResetUsecase,  # Заглушка
        security_service=security_service,
        user_repository=user_repository
    )

    password_reset_confirm_usecase = providers.Factory(
        # PasswordResetConfirmUsecase,  # Заглушка
        security_service=security_service,
        user_repository=user_repository
    )

    # Основные сервисы
    auth_service = providers.Factory(
        AuthService,
        login_usecase=login_usecase,
        register_usecase=register_usecase,
        refresh_token_usecase=refresh_token_usecase,
        logout_usecase=logout_usecase,
        password_reset_usecase=password_reset_usecase,
        password_reset_confirm_usecase=password_reset_confirm_usecase
    )


# Глобальный экземпляр контейнера
container = DIContainer()


def get_auth_service() -> AuthService:
    """Получение сервиса аутентификации из контейнера"""
    return container.auth_service()


def get_security_service() -> SecurityServiceAdapter:
    """Получение сервиса безопасности из контейнера"""
    return container.security_service()


def get_user_repository() -> UserRepositoryAdapter:
    """Получение репозитория пользователей из контейнера"""
    return container.user_repository()


def get_token_repository() -> TokenRepositoryAdapter:
    """Получение репозитория токенов из контейнера"""
    return container.token_repository()
