"""
Роуты API для user-service
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.services.user_service.src.database.connection import get_db
from backend.services.user_service.src.models import RefreshToken, User
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

router = APIRouter()


@router.post("/register",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED
             )
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    user_service = UserService(db)

    # Проверка, не существует ли уже пользователь с таким email или username
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
    return user


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Аутентификация пользователя"""
    auth_service = AuthService(db)

    user = auth_service.authenticate_user(
        login_data.username, login_data.password)
    if not user:
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

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """Получение текущего пользователя"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновление данных текущего пользователя"""
    user_service = UserService(db)

    # Обновление только разрешенных полей
    update_data = user_data.model_dump(exclude_unset=True)
    if "password" in update_data:
        # Если пароль меняется, нужно его захешировать
        auth_service = AuthService(db)
        update_data["hashed_password"] = auth_service.get_password_hash(
            update_data.pop("password"))

    # ИСПРАВЛЕНО: передаем update_data вместо user_data
    user = user_service.update_user(current_user.id, update_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Обновление access token через refresh token"""
    auth_service = AuthService(db)

    # Верификация refresh token
    payload = auth_service.verify_token(refresh_data.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверка, что это refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверка, не отозван ли токен
    refresh_token_model = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_data.refresh_token,
        not RefreshToken.is_revoked
    ).first()
    if not refresh_token_model:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token отозван",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Получение пользователя из refresh token
    user = auth_service.get_user_from_token(refresh_data.refresh_token)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Генерация новых токенов
    access_token, new_refresh_token = auth_service.create_tokens(user)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout_user(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Выход из системы (отзыв refresh token)"""
    auth_service = AuthService(db)
    success = auth_service.revoke_refresh_token(refresh_data.refresh_token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token не найден или уже отозван"
        )

    return {"message": "Успешный выход из системы"}


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получение списка пользователей (для админов)"""
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Получение пользователя по ID (для админов)"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user
