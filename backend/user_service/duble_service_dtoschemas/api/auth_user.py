""" API Routers Auth  """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide


from backend.database_service.container import Container
from backend.user_service.duble_service_dtoschemas.factories.auth_service_factory import AuthServiceFactory
from backend.user_service.duble_service_dtoschemas.schemas.auth.login_request import UserLogin


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

    auth_service = AuthServiceFactory.create(db_session)
    access_token, refresh_token = auth_service.authenticate_and_create_tokens(
        login_data.user_name,
        login_data.password
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
