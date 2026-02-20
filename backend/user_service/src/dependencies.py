"""
FastAPI Dependencies для User Service

Этот файл определяет все dependency-функции, которые используются
в роутах user_service. Зависимости от других сервисов (database_service)
подключаются через их get_db_dependency().

Принципы:
- Контейнеры независимы друг от друга
- Зависимости между сервисами через FastAPI Depends
- Репозитории получают сессию через dependency injection
"""

from fastapi import Depends
from sqlalchemy.orm import Session

# Импортируем dependency от database_service
# Контейнеры не зависят друг от друга напрямую!
from backend.user_service.src.container import container
from backend.database_service.src import get_db_dependency
# Импортируем репозитории
from backend.user_service.src.repositories import (
    SQLUserRepository,
    SQLTokenRepository
)
from backend.user_service.src.service import (
    AuthService,
    RegisterService
)

# ==========================================
# ЗАВИСИМОСТИ ОТ БАЗЫ ДАННЫХ
# ==========================================

# Получаем dependency для сессии БД из database_service
db_dependency = get_db_dependency()


# ==========================================
# DEPENDENCIES ДЛЯ РЕПОЗИТОРИЕВ
# ==========================================

def get_user_repository(
    db: Session = Depends(db_dependency)
) -> SQLUserRepository:
    """
    Dependency для получения репозитория пользователей

    Создаёт новый экземпляр репозитория с сессией БД для текущего запроса.

    """
    return SQLUserRepository(db)


def get_token_repository(
    db: Session = Depends(db_dependency)
) -> SQLTokenRepository:
    """
    Dependency для получения репозитория токенов

    Создаёт новый экземпляр репозитория с сессией БД для текущего запроса.

    """
    return SQLTokenRepository(db)


# ==========================================
# DEPENDENCIES ДЛЯ СЕРВИСОВ
# ==========================================

def get_auth_service(
    user_repo: SQLUserRepository = Depends(get_user_repository)
) -> 'AuthService':
    """
    Dependency для получения сервиса аутентификации

    Создаёт экземпляр сервиса с необходимыми репозиториями.
    Конфигурация берётся из DI контейнера user_service.

    """

    # Получаем конфигурации из DI контейнера user_service
    auth_config = container.auth_config()
    api_config = container.api_config()
    password_service = container.password_service()
    jwt_service = container.jwt_service()

    return AuthService(
        user_repo=user_repo,
        password_service=password_service,
        jwt_service=jwt_service,
        auth_config=auth_config,
        api_config=api_config
    )


def get_register_service(
    user_repo: SQLUserRepository = Depends(get_user_repository),
) -> 'RegisterService':
    """
    Dependency для получения сервиса регистрации

    Создаёт экземпляр сервиса с необходимыми репозиториями.
    Конфигурация берётся из DI контейнера user_service.

    """

    # Получаем конфигурации из DI контейнера user_service
    auth_config = container.auth_config()
    password_service = container.password_service()

    return RegisterService(
        user_repo=user_repo,
        password_service=password_service,
        auth_config=auth_config
    )


__all__ = [
    "get_user_repository",
    "get_token_repository",
    "get_auth_service",
    "get_register_service",
]
