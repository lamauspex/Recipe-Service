""" Схемы для входящих запросов аутентификации """

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)


class LoginRequest(BaseModel):
    """
    Схема запроса на вход пользователя

    Используется для аутентификации пользователя
    по email и паролю.

    Attributes:
        email: Email пользователя (валидный формат)
        password: Пароль пользователя
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecureP@ss123"
            }
        }
    )

    email: EmailStr = Field(
        ...,
        description="Email пользователя"
    )
    password: str = Field(
        ...,
        description="Пароль пользователя"
    )


class RefreshTokenRequest(BaseModel):
    """
    Схема запроса на обновление токена

    Используется для получения новой пары токенов
    по истечении срока действия access_token.

    Attributes:
        refresh_token: Refresh токен
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )

    refresh_token: str = Field(
        ...,
        description="Refresh токен"
    )


class LogoutRequest(BaseModel):
    """
    Схема запроса на выход из системы

    Используется для отзыва refresh токена при логауте.

    Attributes:
        refresh_token: Refresh токен для отзыва
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )

    refresh_token: str = Field(
        ...,
        description="Refresh токен для отзыва"
    )
