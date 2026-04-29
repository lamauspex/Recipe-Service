"""
FastAPI Dependencies для User Service

Принципы:
- Единая точка входа для всех зависимостей
- Dependency Injection через FastAPI Depends
- Сессия БД создаётся на каждый запрос и закрывается автоматически
"""


from fastapi import Depends
from sqlalchemy.orm import Session

from backend.service_user.src.infrastructure.container import container
from backend.service_user.src.repositories import (
    SQLUserRepository,
    SQLTokenRepository
)
from backend.service_user.src.service import (
    AuthService,
    RegisterService
)

# ==========================================
# ПОДКЛЮЧЕНИЕ К БД
# ==========================================


def get_db():
    """
    Dependency для получения сессии БД
    """
    session_manager = container.session_manager()
    session = session_manager.SessionLocal()

    try:
        yield session
    finally:
        session.close()


# ==========================================
# РЕПОЗИТОРИИ
# ==========================================

def get_user_repository(
    db: Session = Depends(get_db)
) -> SQLUserRepository:
    """ Dependency для получения репозитория пользователей """
    return SQLUserRepository(db)


def get_token_repository(
    db: Session = Depends(get_db)
) -> SQLTokenRepository:
    """ Dependency для получения репозитория токенов """
    return SQLTokenRepository(db)


# ==========================================
# СЕРВИСЫ
# ==========================================

def get_auth_service(
    user_repo: SQLUserRepository = Depends(get_user_repository),
    token_repo: SQLTokenRepository = Depends(get_token_repository)
) -> 'AuthService':
    """ Dependency для сервиса аутентификации """

    return AuthService(
        user_repo=user_repo,
        token_repo=token_repo,
        password_service=container.password_service(),
        jwt_service=container.jwt_service(),
        auth_config=container.auth_config(),
        auth_validator=container.auth_validator(),
        mapper=container.auth_mapper()
    )


def get_register_service(
    user_repo: SQLUserRepository = Depends(get_user_repository),
) -> 'RegisterService':
    """ Dependency для сервиса регистрации """

    return RegisterService(
        user_repo=user_repo,
        password_service=container.password_service()
    )


__all__ = [
    "get_db",
    "get_user_repository",
    "get_token_repository",
    "get_auth_service",
    "get_register_service",
]
