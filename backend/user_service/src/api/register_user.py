""" API Routers Register """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
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
    db_session: Session = Depends(Provide[container.db_dependency]),
    register_service: RegisterService = Provide[container.register_service]
):
    """Регистрация пользователя"""

    user = register_service.register_user(register_data)

    return UserResponseDTO.model_validate(user)
