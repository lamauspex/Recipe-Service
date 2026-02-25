""" API Routers Register """

from fastapi import APIRouter, Depends

from backend.service_user.src.dependencies import get_register_service
from backend.service_user.src.service import RegisterService
from backend.service_user.src.schemas.register import (
    UserCreate,
    UserResponseDTO
)


# Создаем router
router = APIRouter(
    prefix="/register_users",
    tags=["Register_Service"]
)


@router.post(
    "/register",
    summary="Регистрация пользователя",
    response_model=UserResponseDTO
)
async def register_user(
    register_data: UserCreate,
    register_service: RegisterService = Depends(get_register_service)
):
    """
    Регистрация пользователя
    Сервис возвращает готовый UserResponseDTO
    """

    return register_service.register_user(register_data)
