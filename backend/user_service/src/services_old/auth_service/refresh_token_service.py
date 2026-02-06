"""
Управление refresh-токенами
Обновлено для использования базового класса
"""

from uuid import UUID
from datetime import datetime
from typing import Optional

from backend.user_service.src.repository import RefreshTokenRepository
from common.base_service import BaseService


class RefreshTokenService(BaseService):
    """Класс для работы с refresh-токенами"""

    def __init__(self, db_session):
        super().__init__()
        self.repo = RefreshTokenRepository(db_session)

    def create_refresh_token(self, user_id: UUID, token: str, expires_at: datetime) -> dict:
        """Создание refresh токена"""
        try:
            self.repo.create_refresh_token(
                user_id=user_id,
                token=token,
                expires_at=expires_at
            )
            return self._handle_success("Refresh токен создан")
        except Exception as e:
            return self._handle_error(e, "создания refresh токена")

    def revoke_token(self, token: str) -> dict:
        """Отзыв токена"""
        try:
            success = self.repo.revoke_token(token)
            if success:
                return self._handle_success("Refresh токен отозван")
            else:
                return self._handle_error(Exception("Токен не найден"), "отзыва refresh токена")
        except Exception as e:
            return self._handle_error(e, "отзыва refresh токена")

    def get_valid_token(self, token: str) -> dict:
        """Получение валидного токена"""
        try:
            result = self.repo.get_valid_token(token)
            if result:
                return self._handle_success("Токен валиден", data={"token": result})
            else:
                return self._handle_error(Exception("Токен недействителен"), "проверки refresh токена")
        except Exception as e:
            return self._handle_error(e, "проверки refresh токена")
