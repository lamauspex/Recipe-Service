""" API Routers Register """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.container import container
from backend.user_service.src.schemas.register.register_request import (
    UserRegister)


# Создаем router
router = APIRouter(
    prefix="/register_users",
    tags=["Register_Service"]
)


@router.post(
    "/register",
    summary="Регистрация пользователя"
)
@inject
async def register_user(
    register_data: UserRegister,
    db_session: Session = Depends(Provide[container.db_dependency]),
    register_service=Depends(Provide[container.register_service])
):
    """Регистрация пользователя"""

    user = register_service.register_user(
        register_data.user_name,
        register_data.email,
        register_data.password
    )

    return user.model_dump()
