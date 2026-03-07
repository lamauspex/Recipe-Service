""" API Routers Auth  """

from fastapi import APIRouter, Depends, HTTPException, status

from backend.service_user.src.protocols.token_repository import (
    TokenRepositoryProtocol)
from backend.service_user.src.schemas.auth.requests import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest)
from backend.service_user.src.schemas.auth.responses import (
    MessageResponse,
    TokenResponse)
from backend.service_user.src.service.auth_service import AuthService
from backend.service_user.src.dependencies import (
    get_auth_service,
    get_token_repository)


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
        TokenResponse(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
            token_type="bearer"
        )

    """
    # Вызываем метод аутентификации с распакованными данными
    token_pair = auth_service.authenticate_and_create_tokens(
        email=login_data.email,
        password=login_data.password
    )

    return TokenResponse.model_validate(token_pair.to_repository_dict())


@router.post(
    "/refresh",
    summary="Обновление токенов",
    response_model=TokenResponse
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновление токенов"""

    token_pair = auth_service.refresh_access_token(
        refresh_token=refresh_data.refresh_token
    )

    if not token_pair:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истёкший токен"
        )

    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token
    )


@router.post(
    "/logout",
    summary="Выход из системы",
    response_model=MessageResponse
)
async def logout(
    logout_data: LogoutRequest,
    token_repo: TokenRepositoryProtocol = Depends(get_token_repository)
):
    """Выход из системы (инвалидация refresh токена)"""

    token_repo.revoke_token(logout_data.refresh_token)

    return MessageResponse(message="Вы успешно вышли из системы")
