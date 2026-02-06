"""
Базовые DTO для ответов
"""
from abc import ABC
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class BaseResponseDTO(BaseModel):
    """Базовый DTO для ответов"""
    success: bool = True
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponseDTO(BaseResponseDTO):
    """DTO для ответов с ошибками"""
    success: bool = False
    error_code: str
    details: Optional[Dict[str, Any]] = None


class UserResponseDTO(BaseModel):
    """DTO для данных пользователя"""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class AuthTokensDTO(BaseModel):
    """DTO для токенов авторизации"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class LoginResponseDTO(BaseResponseDTO):
    """DTO для ответа авторизации"""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create_success(cls, user: UserResponseDTO, tokens: AuthTokensDTO) -> "LoginResponseDTO":
        return cls(
            data={
                "user": user.dict(),
                "tokens": tokens.dict()
            }
        )


class RegisterResponseDTO(BaseResponseDTO):
    """DTO для ответа регистрации"""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create_success(cls, user: UserResponseDTO) -> "RegisterResponseDTO":
        return cls(
            data={"user": user.dict()}
        )


class TokenRefreshResponseDTO(BaseResponseDTO):
    """DTO для ответа обновления токена"""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create_success(cls, tokens: AuthTokensDTO) -> "TokenRefreshResponseDTO":
        return cls(
            data={"tokens": tokens.dict()}
        )


class UserListResponseDTO(BaseResponseDTO):
    """DTO для списка пользователей"""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create_success(cls, users: List[UserResponseDTO], total: int, page: int, per_page: int) -> "UserListResponseDTO":
        return cls(
            data={
                "users": [user.dict() for user in users],
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "pages": (total + per_page - 1) // per_page
                }
            }
        )


class UserCreateResponseDTO(BaseResponseDTO):
    """DTO для ответа создания пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create_success(cls, user: UserResponseDTO) -> "UserCreateResponseDTO":
        return cls(
            data={"user": user.dict()}
        )


class UserUpdateResponseDTO(BaseResponseDTO):
    """DTO для ответа обновления пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create_success(cls, user: UserResponseDTO) -> "UserUpdateResponseDTO":
        return cls(
            data={"user": user.dict()}
        )


class UserDeleteResponseDTO(BaseResponseDTO):
    """DTO для ответа удаления пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create_success(cls, user_id: int) -> "UserDeleteResponseDTO":
        return cls(
            data={"deleted_user_id": user_id}
        )


class PasswordResetResponseDTO(BaseResponseDTO):
    """DTO для ответа сброса пароля"""
    data: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create_success(cls, message: str) -> "PasswordResetResponseDTO":
        return cls(
            message=message
        )


class LogoutResponseDTO(BaseResponseDTO):
    """DTO для ответа выхода"""
    @classmethod
    def create_success(cls) -> "LogoutResponseDTO":
        return cls(message="Successfully logged out")