"""
Базовые DTO для запросов
"""


from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from uuid import UUID


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


# === DTO для управления пользователями ===

class UserListRequestDTO(BaseRequestDTO):
    """DTO для получения списка пользователей"""
    page: int = 1
    per_page: int = 10
    search: Optional[str] = None
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None


class UserStatusUpdateRequestDTO(BaseRequestDTO):
    """DTO для обновления статуса пользователя"""
    user_id: UUID
    status: str  # activate, deactivate, lock, unlock
    reason: Optional[str] = None


class UserDeleteRequestDTO(BaseRequestDTO):
    """DTO для удаления пользователя"""
    user_id: UUID


class UserActivityRequestDTO(BaseRequestDTO):
    """DTO для получения активности пользователя"""
    user_id: UUID
    days: int = 30


class UserSearchRequestDTO(BaseRequestDTO):
    """DTO для поиска пользователей"""
    search_term: str
    limit: int = 20


# === DTO для управления role ===

class UserRoleRequestDTO(BaseRequestDTO):
    """DTO для получения ролей пользователей"""
    user_id: UUID
    role: str
