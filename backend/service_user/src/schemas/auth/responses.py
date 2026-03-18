""" Схемы для ответов API аутентификации """


from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class TokenResponse(BaseModel):
    """
    Ответ с парой токенов после успешной аутентификации

    Возвращается при успешном login или refresh

    Attributes:
        access_token: JWT токен доступа
        refresh_token: JWT токен обновления
        token_type: Тип токена (по умолчанию "bearer")
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    )

    access_token: str = Field(
        ...,
        description="JWT токен доступа"
    )
    refresh_token: str = Field(
        ...,
        description="JWT токен обновления"
    )
    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )


class MessageResponse(BaseModel):
    """
    Ответ с текстовым сообщением

    Используется для:
    - Успешного логаута
    - Ошибок валидации
    - Информационных сообщений

    Attributes:
        message: Текст сообщения
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "message": "Успешный выход из системы"
            }
        }
    )

    message: str = Field(
        ...,
        description="Текст сообщения"
    )
