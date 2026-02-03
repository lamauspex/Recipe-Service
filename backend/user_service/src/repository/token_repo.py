"""
Репозиторий для работы с refresh токенами
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID

from backend.user_service.src.models import RefreshToken


class RefreshTokenRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_refresh_token(
        self,
        user_id: UUID,
        token: str,
        expires_at
    ) -> RefreshToken:
        """Создание refresh токена"""

        # Отзываем старые токены пользователя
        self.revoke_user_tokens(user_id)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token

    def get_valid_token(
        self,
        token: str
    ) -> Optional[RefreshToken]:
        """Получение валидного токена"""

        return self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.token == token,
                RefreshToken.is_revoked.is_(False),
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        ).first()

    def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""

        refresh_token = self.get_valid_token(token)
        if refresh_token:
            refresh_token.is_revoked = True
            self.db.commit()
            return True
        return False

    def revoke_user_tokens(self, user_id: UUID) -> None:
        """Отзыв всех токенов пользователя"""

        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).update({"is_revoked": True})
        self.db.commit()

    def cleanup_expired_tokens(self) -> int:
        """Очистка просроченных токенов"""

        expired_count = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.now(timezone.utc)
        ).delete()

        self.db.commit()
        return expired_count
