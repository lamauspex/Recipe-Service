""" Внутренние DTO для аутентификации """

from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict

from backend.service_user.src.schemas.base import (
    DTOConverterMixin,
    UserTimestampsModel
)


class TokenPairDTO(DTOConverterMixin):

    """Пара токенов (сервисный слой)"""

    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str


class AuthResultDTO(DTOConverterMixin):
    """Результат аутентификации"""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )

    user_id: UUID
    user_name: str
    role: str


class RefreshTokenDataDTO(
    DTOConverterMixin,
    UserTimestampsModel
):
    """Данные для refresh токена"""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    token: str
    expires_at: datetime
