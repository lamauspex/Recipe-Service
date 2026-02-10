""" API Routers Auth  """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.container import container
from backend.user_service.src.schemas.auth.login_request import UserLogin


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
    db_session: Session = Depends(Provide[container.db_dependency]),
    auth_service=Depends(Provide[container.auth_service])
):
    """Аутентификация пользователя"""

    token_pair = auth_service.authenticate_and_create_tokens(
        login_data.user_name,
        login_data.password
    )

    return token_pair.model_dump()
