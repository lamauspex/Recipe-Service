"""
Роуты API для user-service
"""
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from backend.user_service.src.middleware import get_current_admin_user
from backend.user_service.src.models import User
from backend.database_service.connection import database
from backend.user_service.src.services import UserService
from backend.user_service.src.schemas import (
    AdminUserResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    UserResponse,
    UserUpdate
)


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users_Service"]
)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получение текущего пользователя"
)
def get_current_user_info(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Получение текущего пользователя через сервис"""
    # Используем сервис для получения актуальных данных пользователя
    user_service = UserService(db)
    user = user_service.get_user(current_user.id)

    # Если пользователь не найден в БД, возвращаем данные из токена
    if not user:
        return current_user

    return user


@router.get(
    "/{user_id}",
    response_model=AdminUserResponse,
    summary="Получение пользователя по ID"
)
def get_user(
    user_id: UUID,
    db: Session = Depends(database.get_db)
):
    """Получение детальной информации о пользователе"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)

    return user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Обновление данных текущего пользователя"
)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(database.get_db)
):
    """Обновление данных текущего пользователя"""

    user_service = UserService(db)
    update_data = user_data.model_dump(exclude_unset=True)
    user = user_service.update_user(current_user.id, update_data)

    return user


@router.post(
    "/password/reset-request",
    summary="Запрос сброса пароля"
)
def request_reset_password(
    reset_data: PasswordResetRequest,
    db: Session = Depends(database.get_db)
):
    """ Отправка email с токеном для сброса пароля """

    user_service = UserService(db)
    success, message = user_service.request_reset_password(reset_data.email)

    return {
        'message': message,
        'success': success,
    }


@router.post(
    "/password/reset-confirm",
    summary="Подтверждение сброса пароля"
)
def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(database.get_db)
):
    """Установка нового пароля по токену"""

    user_service = UserService(db)
    success, message = user_service.confirm_password_reset(
        reset_data.token,
        reset_data.new_password
    )
    return {
        'message': message,
        'success': success,
    }
