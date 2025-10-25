"""
Роуты API для user-service
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from datetime import datetime, timezone
import logging
from uuid import UUID

from backend.services.user_service.src.database.connection import get_db
from backend.services.user_service.src.models import User
from backend.services.user_service.src.schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    UserUpdate, RefreshTokenRequest
)
from backend.services.user_service.src.services.user_service import UserService
from backend.services.user_service.src.services.auth_service import AuthService
from backend.services.user_service.src.middleware.jwt_middleware import (
    get_current_active_user,
    get_current_admin_user
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/health",
            summary="Проверка состояния сервиса",
            )
async def health_check(db: Session = Depends(get_db)):
    """Проверка состояния сервиса и базы данных"""
    try:
        # Проверка подключения к базе данных
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "user-service",
        "database": db_status,
        "version": "1.0.0"
    }


@router.post("/register",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Регистрация нового пользователя"
             )
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    try:
        user_service = UserService(db)

        # Nе существует ли пользователь с таким email/username
        if user_service.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

        if user_service.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким username уже существует"
            )

        # Создание пользователя
        user = user_service.create_user(user_data)
        logger.info(f"New user registered: {user.username}")
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при регистрации пользователя"
        )


@router.post("/login",
             response_model=Token,
             summary="Аутентификация пользователя"
             )
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Аутентификация пользователя"""
    try:
        auth_service = AuthService(db)

        user = auth_service.authenticate_user(
            login_data.username, login_data.password)
        if not user:
            logger.warning(f"Failed login attempt for: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь неактивен"
            )

        # Генерация токенов
        access_token, refresh_token = auth_service.create_tokens(user)
        logger.info(f"User logged in: {user.username}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при аутентификации"
        )


@router.get("/me",
            response_model=UserResponse,
            summary="Получение текущего пользователя"
            )
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Получение текущего пользователя"""
    return current_user


@router.put("/me",
            response_model=UserResponse,
            summary="Обновление данных текущего пользователя"
            )
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление данных текущего пользователя"""
    try:
        user_service = UserService(db)

        # Обновление только разрешенных полей
        if hasattr(user_data, 'model_dump'):
            update_data = user_data.model_dump(exclude_unset=True)
        else:
            update_data = user_data.dict(exclude_unset=True)

        if "password" in update_data:
            # Если пароль меняется, нужно его захешировать
            auth_service = AuthService(db)
            update_data["hashed_password"] = auth_service.get_password_hash(
                update_data.pop("password"))

        user = user_service.update_user(current_user.id, update_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        logger.info(f"User updated: {user.username}")
        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении пользователя"
        )


@router.post("/refresh",
             response_model=Token,
             summary="Обновление access token через refresh token"
             )
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Обновление access token через refresh token"""
    try:
        auth_service = AuthService(db)

        # Верификация refresh token
        payload = auth_service.verify_token(refresh_data.refresh_token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный или просроченный refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Проверяем, что это refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный тип токена",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Проверяем, существует ли и не отозван ли токен
        refresh_token_model = auth_service.refresh_token_repo.get_valid_token(
            refresh_data.refresh_token
        )
        if not refresh_token_model:
            # Дополнительная отладочная информация
            logger.warning(
                f"Refresh token not found or revoked: {refresh_data.refresh_token[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token отозван или недействителен",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Получаем пользователя из refresh token
        user = auth_service.get_user_from_token(refresh_data.refresh_token)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или неактивен",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Отзываем старый refresh token перед созданием нового
        auth_service.revoke_refresh_token(refresh_data.refresh_token)

        # Генерация новых токенов
        access_token, new_refresh_token = auth_service.create_tokens(user)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении токена"
        )


@router.post("/logout",
             summary="Выход из системы (отзыв refresh token)"
             )
async def logout_user(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Выход из системы (отзыв refresh token)"""
    try:
        auth_service = AuthService(db)
        success = auth_service.revoke_refresh_token(refresh_data.refresh_token)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token не найден или уже отозван"
            )

        logger.info("User logged out successfully")
        return {"message": "Успешный выход из системы"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при выходе из системы"
        )


@router.get("/",
            response_model=List[UserResponse],
            summary="Получение списка пользователей (для админов)"
            )
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получение списка пользователей (для админов)"""
    try:
        user_service = UserService(db)
        users = user_service.get_users(skip=skip, limit=limit)
        return users

    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении списка пользователей"
        )


@router.get("/{user_id}",
            response_model=UserResponse,
            summary="Получение пользователя по ID (для админов)"
            )
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получение пользователя по ID (для админов)"""
    try:
        user_service = UserService(db)
        user = user_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении пользователя"
        )
