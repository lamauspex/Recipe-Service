"""
Пример интеграции нового сервиса с API слоем
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from ...services import get_auth_service
from ...services.interfaces.auth import AuthInterface
from ...services.infrastructure.common.exceptions import (
    ServiceException,
    ValidationException,
    UnauthorizedException,
    ConflictException
)
from ...schemas.schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutRequest,
    LogoutResponse
)

# Создаем новый роутер для нового сервиса
new_auth_router = APIRouter(prefix="/api/v2/auth", tags=["auth-v2"])


@new_auth_router.post("/login", response_model=LoginResponse)
async def login_v2(
    request: LoginRequest,
    auth_service: AuthInterface = Depends(get_auth_service)
):
    """
    Авторизация с использованием нового сервиса
    """
    try:
        # Маппинг схем
        login_request = LoginRequestDTO(
            email=request.email,
            password=request.password,
            remember_me=request.remember_me
        )

        # Вызов сервиса
        response = await auth_service.login(login_request)

        # Маппинг ответа обратно к схеме API
        return LoginResponse(
            success=response.success,
            message=response.message,
            data=response.data
        )

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code.value}
        )
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": e.message, "error_code": e.error_code.value}
        )
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "error_code": e.error_code.value}
        )


@new_auth_router.post("/register", response_model=RegisterResponse)
async def register_v2(
    request: RegisterRequest,
    auth_service: AuthInterface = Depends(get_auth_service)
):
    """
    Регистрация с использованием нового сервиса
    """
    try:
        # Маппинг схем
        register_request = RegisterRequestDTO(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone
        )

        # Вызов сервиса
        response = await auth_service.register(register_request)

        # Маппинг ответа обратно к схеме API
        return RegisterResponse(
            success=response.success,
            message=response.message,
            data=response.data
        )

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code.value}
        )
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": e.message, "error_code": e.error_code.value}
        )
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "error_code": e.error_code.value}
        )


@new_auth_router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token_v2(
    request: RefreshTokenRequest,
    auth_service: AuthInterface = Depends(get_auth_service)
):
    """
    Обновление токена с использованием нового сервиса
    """
    try:
        # Маппинг схем
        refresh_request = RefreshTokenRequestDTO(
            refresh_token=request.refresh_token
        )

        # Вызов сервиса
        response = await auth_service.refresh_token(refresh_request)

        # Маппинг ответа обратно к схеме API
        return RefreshTokenResponse(
            success=response.success,
            message=response.message,
            data=response.data
        )

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "error_code": e.error_code.value}
        )
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": e.message, "error_code": e.error_code.value}
        )
    except ServiceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "error_code": e.error_code.value}
        )


@new_auth_router.post("/logout", response_model=LogoutResponse)
async def logout_v2(
    request: LogoutRequest,
    auth_service: AuthInterface = Depends(get_auth_service)
):
    """
    Выход с использованием нового сервиса
    """
    try:
        # Маппинг схем
        logout_request = LogoutRequestDTO(
            refresh_token=request.refresh_token
        )

        # Вызов сервиса
        response = await auth_service.logout(logout_request)

        # Маппинг ответа обратно к схеме API
        return LogoutResponse(
            success=response.success,
            message=response.message
        )

    except ServiceException as e:
        # Выход не должен падать с ошибкой
        return LogoutResponse(success=True, message="Logged out successfully")


# Пример middleware для нового сервиса
async def auth_middleware_v2(request, call_next):
    """
    Пример middleware для аутентификации с новым сервисом
    """
    # Здесь можно добавить логику аутентификации
    # используя новый сервис

    response = await call_next(request)
    return response


"""
Преимущества нового подхода:

1. **Чистая архитектура**: Четкое разделение слоев
2. **Тестируемость**: Легко мокировать зависимости
3. **Расширяемость**: Просто добавлять новые функции
4. **Согласованность**: Единые паттерны и интерфейсы
5. **Обработка ошибок**: Централизованная и типизированная
6. **DI контейнер**: Современное управление зависимостями

Пример использования в тестах:

```python
import pytest
from unittest.mock import AsyncMock
from services_new import get_auth_service
from services_new.infrastructure.common.exceptions import ValidationException

@pytest.mark.asyncio
async def test_login_success():
    # Мок зависимостей
    user_repository = AsyncMock()
    security_service = AsyncMock()
    token_repository = AsyncMock()
    
    # Настройка моков
    user_repository.get_by_email.return_value = mock_user
    security_service.verify_password.return_value = True
    security_service.generate_access_token.return_value = "fake_token"
    security_service.generate_refresh_token.return_value = "fake_refresh"
    
    # Тест
    auth_service = get_auth_service()
    response = await auth_service.login(login_request)
    
    assert response.success == True
    assert "tokens" in response.data
```"""
