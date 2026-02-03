
"""
Admin_schemas для администрирования
"""

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)
from typing import Optional
from uuid import UUID
from datetime import datetime

from backend.user_service.src.schemas.schemas import UserResponse
from backend.user_service.src.schemas.user_roles import UserRole


class AdminUserResponse(UserResponse):
    """Схема для ответа админов"""

    email_verified: bool
    last_login: Optional[datetime] = None
    login_count: int = Field(
        default=0,
        ge=0
    )

    model_config = ConfigDict(from_attributes=True)


class AdminActionRequest(BaseModel):
    """Запрос административного действия"""

    target_user_id: UUID
    action: str = Field(
        ...,
        min_length=1,
        max_length=50
    )
    value: Optional[str] = Field(
        default=None,
        max_length=255
    )
    reason: Optional[str] = Field(
        default=None,
        max_length=500
    )

    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        allowed_actions = [
            'activate',
            'deactivate',
            'verify_email',
            'unverify_email'
        ]
        if v not in allowed_actions:
            raise ValueError(
                f'Action must be one of: {allowed_actions}'
            )
        return v


class RoleUpdateRequest(BaseModel):
    """Запрос на изменение роли пользователя"""

    user_id: UUID
    new_role: UserRole
    reason: Optional[str] = Field(
        default=None,
        max_length=500
    )


class AdminStatsResponse(BaseModel):
    """Статистика системы для админов"""

    total_users: int = Field(..., ge=0)
    active_users: int = Field(..., ge=0)
    admin_users: int = Field(..., ge=0)
    moderator_users: int = Field(..., ge=0)
    verified_users: int = Field(..., ge=0)
    recent_registrations: int = Field(..., ge=0)
