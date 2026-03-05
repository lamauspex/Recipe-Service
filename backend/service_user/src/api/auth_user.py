""" API Routers Auth  """

from fastapi import APIRouter, Depends, HTTPException, status

from backend.service_user.src.schemas.auth.requests import LoginRequest
from backend.service_user.src.schemas.auth.responses import TokenResponse
from backend.service_user.src.service.auth_service import AuthService
from backend.service_user.src.dependencies import get_auth_service


# Создаем router
router = APIRouter(
    prefix="/auth_users",
    tags=["Auth_Service"]
)


@router.post(
    "/login",
    summary="Аутентификация пользователя",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Неверные учетные данные"},
        404: {"description": "Пользователь не найден"},
        422: {"description": "Ошибка валидации данных"}
    }
)
async def login_user(
    login_data: LoginRequest,
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
        email=login_data.email,
        password=login_data.password
    )

    if not token_pair:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return TokenResponse.model_validate(token_pair)
