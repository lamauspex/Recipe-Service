""" API Routers Auth  """


from fastapi import APIRouter, Depends, status


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
from backend.service_user.src.infrastructure.dependencies import (
    get_auth_service,
    get_token_repository)


# Создаем router
router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/login",
    summary="Аутентификация пользователя",
    description="Вход в систему с помощью email и пароля",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Неверные учетные данные"}
    }
)
async def login_user(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Аутентификация и создание токенов

    - **email**: Email пользователя
    - **password**: Пароль

    Возвращает access и refresh токены
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
    description="Обновление access токена с помощью refresh токена.",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Неверный или истёкший токен"}
    }
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Обновление токенов

    - **refresh_token**: Текущий refresh токен

    Возвращает новую пару токенов
    """

    token_pair = auth_service.refresh_access_token(
        refresh_token=refresh_data.refresh_token
    )

    return TokenResponse(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token
    )


@router.post(
    "/logout",
    summary="Выход из системы",
    description="Инвалидация refresh токена. Пользователь выходит из системы.",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK
)
async def logout(
    logout_data: LogoutRequest,
    token_repo: TokenRepositoryProtocol = Depends(get_token_repository)
):
    """Выход из системы (инвалидация refresh токена)"""

    token_repo.revoke_token(logout_data.refresh_token)
    return MessageResponse(message="Вы успешно вышли из системы")
