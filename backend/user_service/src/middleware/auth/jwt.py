"""JWT аутентификация - только работа с токенами"""

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from backend.user_service.src.models import User
from backend.database_service.connection import database
from backend.user_service.src.services_old import JWTService
from backend.user_service.src.repository import UserRepository
from backend.user_service.src.config import settings
from backend.user_service.src.exceptions import (
    AuthException,
    ForbiddenException
)
from backend.user_service.src.middleware.logging import BusinessEventLogger
from backend.user_service.src.middleware.logging.utils_trace_id import get_trace_id

# Используем auto_error=False для обработки случаев, когда токен отсутствует
security = HTTPBearer(auto_error=False)


class JWTBearer(HTTPBearer):
    """Класс для JWT Bearer аутентификации"""

    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request):
        credentials = await super().__call__(request)
        if credentials:
            # Проверка формата токена может быть добавлена здесь
            return credentials
        return None


class AdminBearer(HTTPBearer):
    """Класс для администраторской JWT Bearer аутентификации"""

    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request):
        credentials = await super().__call__(request)
        if credentials:
            # Дополнительная проверка прав
            # администратора может быть добавлена здесь
            return credentials
        return None


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(database.get_db)
) -> User:
    """Получение текущего пользователя из JWT токена"""

    # Проверяем, есть ли токен
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Функция для получения IP
    def get_client_ip():
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else None

    try:
        # Декодируем токен с помощью JWTService
        jwt_service = JWTService(
            settings.auth.SECRET_KEY,
            settings.auth.ALGORITHM
        )
        payload = jwt_service.decode_token(credentials.credentials)

        if not payload:
            # Логируем неудачную попытку
            BusinessEventLogger.log_auth_event(
                username="unknown",
                success=False,
                failure_reason="Неверный или просроченный токен",
                ip_address=get_client_ip(),
                user_agent=request.headers.get("user-agent"),
                trace_id=get_trace_id()
            )
            raise AuthException("Неверный или просроченный токен")

        # Получаем user_id из payload
        user_id = payload.get("sub")
        if not user_id:
            # Логируем ошибку
            BusinessEventLogger.log_auth_event(
                username="unknown",
                success=False,
                failure_reason="Неверный токен - отсутствует user_id",
                ip_address=get_client_ip(),
                user_agent=request.headers.get("user-agent"),
                trace_id=get_trace_id()
            )
            raise AuthException("Неверный токен - отсутствует user_id")

        # Получаем пользователя из базы данных
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_id(UUID(user_id))

        if user is None:
            # Пользователь не найден - логируем
            BusinessEventLogger.log_auth_event(
                username=payload.get("email", "unknown"),
                success=False,
                failure_reason="Пользователь не найден",
                ip_address=get_client_ip(),
                user_agent=request.headers.get("user-agent"),
                trace_id=get_trace_id()
            )
            raise AuthException("Пользователь не найден")

        if not user.is_active:
            # Пользователь неактивен - логируем
            BusinessEventLogger.log_auth_event(
                username=user.email,
                success=False,
                failure_reason="Пользователь неактивен",
                user_id=str(user.id),
                ip_address=get_client_ip(),
                user_agent=request.headers.get("user-agent"),
                trace_id=get_trace_id()
            )
            raise ForbiddenException("Пользователь неактивен")

        return user

    except AuthException as e:
        # Перебрасываем исключение - ExceptionHandler
        # сам конвертирует в HTTPException
        raise e

    except ForbiddenException as e:
        # Перебрасываем исключение - ExceptionHandler
        # сам конвертирует в HTTPException
        raise e

    except Exception as e:
        # Неожиданная ошибка - конвертируем в AuthException
        raise AuthException(f"Ошибка аутентификации {e}")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Получение текущего активного пользователя"""

    # Проверка уже делается в get_current_user, но оставляем для ясности
    if not current_user.is_active:
        raise ForbiddenException("Пользователь неактивен")

    return current_user
