""" Схема ответа с данными пользователя """


from datetime import datetime
from typing import List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer
)


class UserResponseDTO(BaseModel):
    """
    DTO для ответа с данными пользователя

    Используется для возврата данных пользователя из API.
    Не содержит чувствительной информации (пароли, токены).

    Attributes:
        id: Уникальный идентификатор пользователя
        user_name: Имя пользователя (уникальное)
        email: Email пользователя
        full_name: Полное имя пользователя (опционально)
        is_active: Активен ли аккаунт
        email_verified: Подтверждён ли email
        role_name: Техническое имя роли
        role_display_name: Отображаемое имя роли
        permissions: Список разрешений пользователя
        login_count: Количество входов
        last_login: Дата последнего входа
        created_at: Дата создания аккаунта
        updated_at: Дата последнего обновления
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
    id: str = Field(
        ...,
        description="Уникальный идентификатор"
    )
    user_name: str = Field(
        ...,
        description="Имя пользователя"
    )
    email: str = Field(
        ...,
        description="Email пользователя"
    )
    full_name: Optional[str] = Field(
        default=None,
        description="Полное имя"
    )

    # ========== Статус ==========
    is_active: bool = Field(
        ...,
        description="Активен ли аккаунт"
    )
    email_verified: bool = Field(
        ...,
        description="Подтверждён ли email"
    )

    # ========== Роль (одна роль) ==========
    role_name: str = Field(
        ...,
        description="Техническое имя роли"
    )
    role_display_name: str = Field(
        ...,
        description="Отображаемое имя роли"
    )
    permissions: List[str] = Field(
        ...,
        description="Список разрешений"
    )

    # ========== Статистика ==========
    login_count: int = Field(
        default=0,
        description="Количество входов"
    )
    last_login: Optional[datetime] = Field(
        default=None,
        description="Дата последнего входа"
    )

    # ========== Временные метки ==========
    created_at: datetime = Field(
        ...,
        description="Дата создания"
    )
    updated_at: datetime = Field(
        ...,
        description="Дата обновления"
    )

    # ========== Сериализаторы ==========

    @field_serializer('id')
    def serialize_id(self, value: str, _info) -> str:
        """Сериализация UUID в строку"""
        return str(value)

    @field_serializer('last_login', 'created_at', 'updated_at')
    def serialize_datetime(
        self,
        value: Optional[datetime],
        _info
    ) -> Optional[str]:
        """Сериализация datetime в ISO формат"""
        return value.isoformat() if value else None
