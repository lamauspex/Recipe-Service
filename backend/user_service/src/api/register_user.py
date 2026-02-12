""" API Routers Register """

from fastapi import APIRouter
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.container import container
from backend.user_service.src.service import RegisterService
from backend.user_service.src.schemas.register import (
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
@inject
async def register_user(
    register_data: UserCreate,
    register_service: RegisterService = Provide[container.register_service]
):
    """
    Регистрация пользователя
    Сервис возвращает готовый UserResponseDTO
    """

    return register_service.register_user(register_data)
