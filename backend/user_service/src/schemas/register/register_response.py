""" Схема ответа с данными пользователя """

from pydantic import BaseModel, ConfigDict, field_serializer
from datetime import datetime
from typing import List, Optional


class UserResponseDTO(BaseModel):
    """
    Схема ответа с данными пользователя.

    Используется для возврата данных из API.
    Не содержит чувствительной информации (пароль, токены).
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_name": "john_doe",
                    "email": "john@example.com",
                    "full_name": "John Doe",
                    "is_active": True,
                    "email_verified": False,
                    "role_name": "user",
                    "role_display_name": "Пользователь",
                    "permissions": ["READ"],
                    "login_count": 0,
                    "last_login": None,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
    )

    # ========== Основные данные ==========
    id: str
    user_name: str
    email: str
    full_name: Optional[str] = None

    # ========== Статус ==========
    is_active: bool
    email_verified: bool

    # ========== Роль (одна роль) ==========
    role_name: str
    role_display_name: str
    permissions: List[str]

    # ========== Статистика ==========
    login_count: int = 0
    last_login: Optional[datetime] = None

    # ========== Временные метки ==========
    created_at: datetime
    updated_at: datetime

    # ========== Сериализаторы ==========

    @field_serializer('id')
    def serialize_id(self, value: str, _info) -> str:
        """Сериализация UUID в строку"""
        return str(value)

    @field_serializer('last_login', 'created_at', 'updated_at')
    def serialize_datetime(
        self,
        value: Optional[datetime], _info
    ) -> Optional[str]:
        """Сериализация datetime в ISO формат"""
        return value.isoformat() if value else None
