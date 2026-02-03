""" API Routers Auth  """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from backend.database_service.connection import database
from backend.user_service.src.services import AuthService
from backend.user_service.src.schemas import (
    UserLogin,
    PasswordResetConfirm,
    RefreshTokenRequest
)

# Создаем router
router = APIRouter(
    prefix="/auth_users",
    tags=["Auth_Service"]
)


@router.post(
    "/login",
    summary="Аутентификация пользователя"
)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(database.get_db)
):

    auth_service = AuthService(db)
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
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(database.get_db)
):

    auth_service = AuthService(db)
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
async def logout_user(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(database.get_db)
):

    auth_service = AuthService(db)
    auth_service.revoke_refresh_token(refresh_data.refresh_token)
    return {"message": "Успешный выход из системы"}


@router.post(
    "/reset_password",
    summary="Сброс пароля по токену"
)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(database.get_db)
):

    user_service = AuthService(db)
    success, message = user_service.reset_password(
        reset_data.token,
        reset_data.new_password
    )
    return {"message": message}
