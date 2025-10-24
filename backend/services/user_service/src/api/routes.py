"""
Роуты API для user-service
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.services.user_service.src.database.connection import get_db
from backend.services.user_service.src.schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    UserUpdate, RefreshTokenRequest
)
from backend.services.user_service.src.services.auth_service import (
    AuthService,
    UserService
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
    db: Session = Depends(get_db)
):
    """Получение текущего пользователя
    (заглушка - нужно реализовать JWT валидацию)
    """
    # TODO: Реализовать JWT валидацию и получение текущего пользователя
    # Пока возвращаем тестового пользователя
    user_service = UserService(db)
    test_user = user_service.get_user_by_username("test_user")
    if not test_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return test_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    """Обновление данных текущего пользователя"""
    # TODO: Реализовать JWT валидацию и обновление текущего пользователя
    user_service = UserService(db)

    # Заглушка - обновляем пользователя с ID=1
    user = user_service.update_user(1, user_data)
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
    # TODO: Реализовать валидацию refresh token и генерацию новых токенов
    auth_service = AuthService(db)

    # Заглушка - возвращаем новые токены
    access_token, refresh_token = auth_service.create_test_tokens()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получение списка пользователей (для админов)"""
    user_service = UserService(db)
    users = user_service.get_users(skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Получение пользователя по ID"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user
