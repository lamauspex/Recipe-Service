""" API Routers Auth  """

from fastapi import APIRouter, Depends, status

from backend.user_service.src.schemas.auth.login_request import UserLogin
from backend.user_service.src.schemas.auth.login_response import (
    LoginResponseDTO
)
from backend.user_service.src.service.auth_service import AuthService
from backend.user_service.src.dependencies import get_auth_service


# Создаем router
router = APIRouter(
    prefix="/auth_users",
    tags=["Auth_Service"]
)


@router.post(
    "/login",
    summary="Аутентификация пользователя",
    response_model=LoginResponseDTO,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Неверные учетные данные"},
        404: {"description": "Пользователь не найден"},
        422: {"description": "Ошибка валидации данных"}
    }
)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Проверяет учетные данные пользователя и возвращает пару токенов
    (access + refresh) при успешной аутентификации.

    Args:
        login_data: Данные для входа (имя пользователя + пароль)
        auth_service: Сервис аутентификации (внедряется через Depends)

    Returns:
        LoginResponseDTO: Пара токенов (access + refresh)

    """
    # Вызываем метод аутентификации с распакованными данными
    token_pair = auth_service.authenticate_and_create_tokens(
        user_name=login_data.user_name,
        password=login_data.password
    )

    return LoginResponseDTO.model_validate(token_pair)
