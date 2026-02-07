
"""
Управление refresh-токенами
"""


from uuid import UUID
from datetime import datetime
from typing import Optional

from user_service.repository import RefreshTokenRepository


class RefreshTokenService:
    """ Класс для работы с refresh-токенами """

    def __init__(self, db_session):
        self.repo = RefreshTokenRepository(db_session)

    def create_refresh_token(
        self,
        user_id: UUID,
        token: str,
        expires_at: datetime
    ) -> None:
        """  """

        self.repo.create_refresh_token(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )

    def revoke_token(self, token: str) -> bool:
        """  """

        return self.repo.revoke_token(token)

    def get_valid_token(self, token: str) -> Optional[str]:
        """  """

        return self.repo.get_valid_token(token)
