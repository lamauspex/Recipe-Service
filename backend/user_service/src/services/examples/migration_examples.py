"""
Примеры миграции API роутеров для использования нового сервиса
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

# Импорты из старого сервиса
from ...services_old.auth_service.auth_service import AuthService as OldAuthService

# Импорты из нового сервиса
from ...services import get_auth_service, get_user_service, get_security_service
from ...services.interfaces.auth import AuthInterface
from ...services.interfaces.user import UserInterface
from ...services.interfaces.security import SecurityInterface

# Схемы (остаются те же)
from ...schemas.schemas import (
    LoginRequest, LoginResponse,
    RegisterRequest, RegisterResponse,
    RefreshTokenRequest, RefreshTokenResponse,
    LogoutRequest, LogoutResponse,
    UserCreateRequest, UserCreateResponse,
    UserUpdateRequest, UserUpdateResponse,
    UserListResponse
)

# Создаем новые роутеры для v2 API
auth_router_v2 = APIRouter(prefix="/api/v2/auth", tags=["auth-v2"])
user_router_v2 = APIRouter(prefix="/api/v2/users", tags=["users-v2"])


# =============================================================================
# AUTH ROUTERS V2 - Новый сервис
# =============================================================================

@auth_router_v2.post("/login", response_model=LoginResponse)
async def login_v2(
    request: LoginRequest,
    auth_service: AuthInterface = Depends(get_auth_service)
):
    """
    Авторизация с использованием нового сервиса аутентификации

    Преимущества нового сервиса:
    - Единообразная обработка ошибок
    - Лучшая типизация
    - Четкое разделение ответственности
    """
    try:
        # Маппинг в DTO нового сервиса
        from ...services.dto.requests import LoginRequestDTO

        login_request = LoginRequestDTO(
            email=request.email,
            password=request.password,
            remember_me=request.remember_me
        )

        # Вызов нового сервиса
        response = await auth_service.login(login_request)

        # Маппинг обратно к схеме API
        return LoginResponse(
            success=response.success,
            message=response.message,
            data=response.data
        )

    except Exception as e:
        # Новая система обработки ошибок
        error_mapping = {
            "ValidationException": (status.HTTP_400_BAD_REQUEST, "VALIDATION_ERROR"),
            "UnauthorizedException": (status.HTTP_401_UNAUTHORIZED, "INVALID_CREDENTIALS"),
            "ConflictException": (status.HTTP_409_CONFLICT, "CONFLICT"),
        }

        error_class = type(e).__name__
        if error_class in error_mapping:
            status_code, error_code = error_mapping[error_class]
            raise HTTPException(
                status_code=status_code,
                detail={
                    "message": str(e),
                    "error_code": error_code,
                    "success": False
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                    "success": False
                }
            )


@auth_router_v2.post("/register", response_model=RegisterResponse)
async def register_v2(
    request: RegisterRequest,
    auth_service: AuthInterface = Depends(get_auth_service)
):
    """
    Регистрация с использованием нового сервиса
    """
    try:
        from ...services.dto.requests import RegisterRequestDTO

        register_request = RegisterRequestDTO(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone
        )

        response = await auth_service.register(register_request)

        return RegisterResponse(
            success=response.success,
            message=response.message,
            data=response.data
        )

    except Exception as e:
        error_mapping = {
            "ValidationException": (status.HTTP_400_BAD_REQUEST, "VALIDATION_ERROR"),
            "ConflictException": (status.HTTP_409_CONFLICT, "USER_ALREADY_EXISTS"),
        }

        error_class = type(e).__name__
        if error_class in error_mapping:
            status_code, error_code = error_mapping[error_class]
            raise HTTPException(
                status_code=status_code,
                detail={
                    "message": str(e),
                    "error_code": error_code,
                    "success": False
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                    "success": False
                }
            )


@auth_router_v2.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token_v2(
    request: RefreshTokenRequest,
    auth_service: AuthInterface = Depends(get_auth_service)
):
    """
    Обновление токена с использованием нового сервиса
    """
    try:
        from ...services.dto.requests import RefreshTokenRequestDTO

        refresh_request = RefreshTokenRequestDTO(
            refresh_token=request.refresh_token
        )

        response = await auth_service.refresh_token(refresh_request)

        return RefreshTokenResponse(
            success=response.success,
            message=response.message,
            data=response.data
        )

    except Exception as e:
        error_mapping = {
            "ValidationException": (status.HTTP_400_BAD_REQUEST, "VALIDATION_ERROR"),
            "UnauthorizedException": (status.HTTP_401_UNAUTHORIZED, "INVALID_TOKEN"),
        }

        error_class = type(e).__name__
        if error_class in error_mapping:
            status_code, error_code = error_mapping[error_class]
            raise HTTPException(
                status_code=status_code,
                detail={
                    "message": str(e),
                    "error_code": error_code,
                    "success": False
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Internal server error",
                    "error_code": "INTERNAL_ERROR",
                    "success": False
                }
            )


@auth_router_v2.post("/logout", response_model=LogoutResponse)
async def logout_v2(
    request: LogoutRequest,
    auth_service: AuthInterface = Depends(get_auth_service)
):
    """
    Выход с использованием нового сервиса
    """
    try:
        from ...services.dto.requests import LogoutRequestDTO

        logout_request = LogoutRequestDTO(
            refresh_token=request.refresh_token
        )

        response = await auth_service.logout(logout_request)

        return LogoutResponse(
            success=response.success,
            message=response.message
        )

    except Exception as e:
        # Выход не должен падать с ошибкой
        return LogoutResponse(
            success=True,
            message="Logged out successfully"
        )


# =============================================================================
# USER ROUTERS V2 - Новый сервис
# =============================================================================

@user_router_v2.get("/", response_model=UserListResponse)
async def get_users_v2(
    page: int = 1,
    per_page: int = 10,
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    user_service: UserInterface = Depends(get_user_service)
):
    """
    Получение списка пользователей с новым сервисом
    """
    try:
        response = await user_service.get_users(
            page=page,
            per_page=per_page,
            search=search,
            role=role,
            is_active=is_active
        )

        return UserListResponse(
            success=response.success,
            message=response.message,
            data=response.data
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to fetch users",
                "error_code": "INTERNAL_ERROR",
                "success": False
            }
        )


@user_router_v2.post("/", response_model=UserCreateResponse)
async def create_user_v2(
    request: UserCreateRequest,
    user_service: UserInterface = Depends(get_user_service)
):
    """
    Создание пользователя с новым сервисом
    """
    try:
        from ...services.dto.requests import UserCreateRequestDTO

        create_request = UserCreateRequestDTO(
            email=request.email,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            role=request.role,
            is_active=request.is_active
        )

        response = await user_service.create_user(create_request)

        return UserCreateResponse(
            success=response.success,
            message=response.message,
            data=response.data
        )

    except Exception as e:
        error_mapping = {
            "ValidationException": (status.HTTP_400_BAD_REQUEST, "VALIDATION_ERROR"),
            "ConflictException": (status.HTTP_409_CONFLICT, "USER_ALREADY_EXISTS"),
        }

        error_class = type(e).__name__
        if error_class in error_mapping:
            status_code, error_code = error_mapping[error_class]
            raise HTTPException(
                status_code=status_code,
                detail={
                    "message": str(e),
                    "error_code": error_code,
                    "success": False
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Failed to create user",
                    "error_code": "INTERNAL_ERROR",
                    "success": False
                }
            )


# =============================================================================
# СРАВНЕНИЕ СТАРОГО И НОВОГО ПОДХОДОВ
# =============================================================================

"""
СРАВНЕНИЕ ПОДХОДОВ:

Старый подход (services_old):
- Смешанная ответственность в сервисах
- Разные форматы ответов
- Сложная обработка ошибок
- Тесная связь с внешними зависимостями
- Сложное тестирование

Новый подход (services_new):
- Четкое разделение слоев (usecases, services, repositories)
- Единые DTO для всех операций
- Централизованная обработка исключений
- Слабая связанность через интерфейсы
- Легкое тестирование с моками

ПРИМЕР МИГРАЦИИ РОУТЕРА:

Старый роутер:
```python
@auth_router.post("/login")
async def login_old(request: LoginRequest):
    auth_service = get_auth_service_old()
    return await auth_service.login(request)
```

Новый роутер:
```python
@auth_router_v2.post("/login")
async def login_new(request: LoginRequest):
    auth_service = get_auth_service()  # Новый сервис
    return await auth_service.login(request)
```

ПРЕИМУЩЕСТВА НОВОГО ПОДХОДА:

1. **Типобезопасность**: Все DTO типизированы
2. **Обработка ошибок**: Единообразная и предсказуемая
3. **Тестируемость**: Легко мокировать зависимости
4. **Расширяемость**: Просто добавлять новую функциональность
5. **Поддержка**: Легче понимать и отлаживать код
6. **Стандартизация**: Единые паттерны и подходы

ПЛАН МИГРАЦИИ:

1. ✅ Создать новый сервисный слой
2. ✅ Создать v2 роутеры для тестирования
3. 🔄 Протестировать новую функциональность
4. 🔄 Постепенно мигрировать существующие роутеры
5. 🔄 Удалить старый сервис после полной миграции
"""
