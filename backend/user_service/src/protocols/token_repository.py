

from typing import Protocol, Optional
from uuid import UUID

from backend.user_service.src.models.token import (
    RefreshToken)


class TokenRepositoryProtocol(Protocol):
    """
    Protocol (интерфейс) для репозитория токенов
    """

    def create_refresh_token(
        self,
        user_id: UUID,
        token: str,
        expires_at
    ) -> RefreshToken:
        """Создание refresh токена"""
        ...

    def get_valid_token(
        self,
        token: str
    ) -> Optional[RefreshToken]:
        """Получение валидного токена"""
        ...

    def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""
        ...

    def revoke_user_tokens(self, user_id: UUID) -> None:
        """Отзыв всех токенов пользователя"""
        ...

    def cleanup_expired_tokens(self) -> int:
        """Очистка просроченных токенов"""
        ...
