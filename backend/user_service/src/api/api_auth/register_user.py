""" API Routers Регистрации  """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from backend.user_service.duble_service_dtoschemas.schemas import UserCreate
from backend.user_service.duble_service_dtoschemas.service import (
    RegisterService
)
from backend.database_service.container import Container


# Создаем router
router = APIRouter(
    prefix="/auth_users",
    tags=["Auth_Service"]
)


@router.post(
    "/register",
    summary="Регистрация пользователя"
)
@inject
async def register_user(
    user_data: UserCreate,
    db_session: Session = Depends(Provide[Container.db_dependency])
):
    """Регистрация пользователя"""

    register_service = RegisterService(db_session)
    return register_service.register_user(user_data)
