from datetime import datetime

from backend.user_service.src.models.user_models import User
from backend.user_service.src.schemas.auth.auth_dto import (
    AuthResultDTO,
    TokenPairDTO,
    RefreshTokenDataDTO
)


class AuthMapper:
    """Маппер для аутентификации"""

    @staticmethod
    def user_to_auth_result(user: User) -> AuthResultDTO:
        """Конвертация User в AuthResultDTO"""
        return AuthResultDTO(
            user_id=user.id,
            user_name=user.user_name,
            role=user.role.value
        )

    @staticmethod
    def to_token_pair(
        access_token: str,
        refresh_token: str
    ) -> TokenPairDTO:
        """Конвертация токенов в TokenPairDTO"""
        return TokenPairDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )

    @staticmethod
    def to_refresh_token_data(
        user_id: int,
        token: str,
        expires_at: datetime
    ) -> RefreshTokenDataDTO:
        """Конвертация данных для refresh токена"""
        return RefreshTokenDataDTO(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
