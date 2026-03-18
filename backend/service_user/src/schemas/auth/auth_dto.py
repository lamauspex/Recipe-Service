""" Внутренние DTO для аутентификации (сервисный слой) """


from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)

from backend.service_user.src.schemas.base import DTOConverterMixin


class TokenPairDTO(
    BaseModel,
    DTOConverterMixin
):
    """
    DTO для передачи пары токенов между сервисами

    Используется в сервисном слое для передачи
    сгенерированных токенов.

    Attributes:
        access_token: JWT access токен
        refresh_token: JWT refresh токен
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )

    access_token: str = Field(
        ...,
        description="JWT access токен"
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh токен"
    )


class AuthResultDTO(
    BaseModel,
    DTOConverterMixin
):
    """
    DTO с результатом успешной аутентификации

    Возвращается после проверки credentials
    Содержит базовую информацию о пользователе

    Attributes:
        user_id: Уникальный идентификатор пользователя
        user_name: Имя пользователя (user_name)
        role: Роль пользователя (user, moderator, admin)
    """

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_name": "john_doe",
                "role": "user"
            }
        }
    )

    user_id: UUID = Field(
        ...,
        description="ID пользователя"
    )
    user_name: str = Field(
        ...,
        description="Имя пользователя"
    )
    role: str = Field(
        ...,
        description="Роль пользователя"
    )


class RefreshTokenDataDTO(
    BaseModel,
    DTOConverterMixin
):
    """
    DTO для данных refresh токена.

    Используется для:
    - Проверки валидности токена
    - Хранения данных в БД
    - Проверки срока действия

    Attributes:
        user_id: ID пользователя-владельца токена
        token: Значение refresh токена
        expires_at: Дата и время истечения токена
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "expires_at": "2026-03-18T10:00:00Z"
            }
        }
    )

    user_id: UUID = Field(
        ...,
        description="ID пользователя"
    )
    token: str = Field(
        ...,
        description="Значение токена"
    )
    expires_at: datetime = Field(
        ...,
        description="Срок действия токена"
    )
