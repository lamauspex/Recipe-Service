""" API Routers Регистрации  """

from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from backend.database_service.container import Container
from backend.user_service.duble_service_dtoschemas.schemas import (
    UserCreate
)
from backend.user_service.duble_service_dtoschemas.factories import (
    RegisterServiceFactory
)


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
    db_session=Depends(Provide[Container.db_dependency])
):
    """Регистрация пользователя"""

    register_service = RegisterServiceFactory(db_session)
    return register_service.register_user(user_data)
