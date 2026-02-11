""" API Routers Auth  """

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency_injector.wiring import inject, Provide

from backend.user_service.src.container import container
from backend.user_service.src.schemas.auth.login_request import UserLogin
from backend.user_service.src.schemas.auth.login_response import (
    LoginResponseDTO)
from backend.user_service.src.service.auth_service import AuthService


# Создаем router
router = APIRouter(
    prefix="/auth_users",
    tags=["Auth_Service"]
)


@router.post(
    "/login",
    summary="Аутентификация пользователя",
    response_model=LoginResponseDTO
)
@inject
async def login_user(
    login_data: UserLogin,
    db_session: Session = Depends(Provide[container.db_dependency]),
    auth_service: AuthService = Provide[container.auth_service]
):
    """Аутентификация пользователя"""

    token_pair = auth_service.authenticate_and_create_tokens(login_data)

    return LoginResponseDTO.model_validate(token_pair)
