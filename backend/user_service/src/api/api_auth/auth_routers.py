""" API Routers Auth  """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.services_old import AuthService
from backend.user_service.src.schemas import (
    UserLogin,
    PasswordResetConfirm,
    RefreshTokenRequest
)
from backend.database_service.container import Container


# Создаем router
router = APIRouter(
    prefix="/auth_users",
    tags=["Auth_Service"]
)


@router.post(
    "/login",
    summary="Аутентификация пользователя"
)
@inject
async def login_user(
    login_data: UserLogin,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Аутентификация пользователя"""

    auth_service = AuthService(db_session)
    access_token, refresh_token = auth_service.authenticate_and_create_tokens(
        login_data.user_name,
        login_data.password
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post(
    "/refresh",
    summary="Обновление access token через refresh token"
)
@inject
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Обновление access token через refresh token"""

    auth_service = AuthService(db_session)
    access_token, new_refresh_token = auth_service.refresh_access_token(
        refresh_data.refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post(
    "/logout",
    summary="Выход из системы (отзыв refresh token)"
)
@inject
async def logout_user(
    refresh_data: RefreshTokenRequest,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Выход из системы (отзыв refresh token)"""

    auth_service = AuthService(db_session)
    return auth_service.revoke_refresh_token(refresh_data.refresh_token)


@router.post(
    "/reset_password",
    summary="Сброс пароля по токену"
)
@inject
async def reset_password(
    reset_data: PasswordResetConfirm,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Сброс пароля по токену"""

    auth_service = AuthService(db_session)
    return auth_service.reset_password(
        reset_data.token,
        reset_data.new_password
    )
