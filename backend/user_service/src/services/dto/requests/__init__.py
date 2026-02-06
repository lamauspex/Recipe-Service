"""
Базовые DTO для запросов
"""
from abc import ABC
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr


class BaseRequestDTO(BaseModel):
    """Базовый DTO для запросов"""
    metadata: Optional[Dict[str, Any]] = None


class LoginRequestDTO(BaseRequestDTO):
    """DTO для запроса авторизации"""
    email: EmailStr
    password: str
    remember_me: bool = False


class RegisterRequestDTO(BaseRequestDTO):
    """DTO для запроса регистрации"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None


class RefreshTokenRequestDTO(BaseRequestDTO):
    """DTO для запроса обновления токена"""
    refresh_token: str


class LogoutRequestDTO(BaseRequestDTO):
    """DTO для запроса выхода"""
    refresh_token: Optional[str] = None


class UserCreateRequestDTO(BaseRequestDTO):
    """DTO для создания пользователя"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str = "user"
    is_active: bool = True


class UserUpdateRequestDTO(BaseRequestDTO):
    """DTO для обновления пользователя"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserChangePasswordRequestDTO(BaseRequestDTO):
    """DTO для смены пароля"""
    current_password: str
    new_password: str


class PasswordResetRequestDTO(BaseRequestDTO):
    """DTO для запроса сброса пароля"""
    email: EmailStr


class PasswordResetConfirmRequestDTO(BaseRequestDTO):
    """DTO для подтверждения сброса пароля"""
    token: str
    new_password: str