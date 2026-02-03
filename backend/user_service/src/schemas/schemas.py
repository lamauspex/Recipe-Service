"""
Схемы Pydantic для user-service
Автономная реализация без зависимостей от общих модулей
"""

from pydantic import (
    BaseModel,
    EmailStr,
    field_validator,
    ConfigDict
)
from typing import Optional
from uuid import UUID
from datetime import datetime

from user_service.schemas.user_roles import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    user_name: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""

    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError(
                'Пароль должен содержать минимум 8 символов'
            )
        if not any(c.isupper() for c in v):
            raise ValueError(
                'Пароль должен содержать хотя бы одну заглавную букву'
            )
        if not any(c.isdigit() for c in v):
            raise ValueError(
                'Пароль должен содержать хотя бы одну цифру'
            )
        return v

    @field_validator('user_name')
    @classmethod
    def validate_user_name(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError(
                'Имя пользователя должно содержать минимум 3 символа'
            )

        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                'Имя пользователя может содержать только буквы, '
                'цифры, дефис и подчёркивание'
            )
        return v.strip()


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""

    user_name: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""

    id: UUID
    bio: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
