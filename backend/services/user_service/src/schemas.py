"""
Схемы Pydantic для user-service
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {'from_attributes': True}


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    username: str
    password: str


class Token(BaseModel):
    """Схема токена доступа"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Схема данных из токена"""
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Схема для сброса пароля"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Схема для подтверждения сброса пароля"""
    token: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v
