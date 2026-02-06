"""
Интерфейсы репозиториев для работы с токенами
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from backend.user_service.src.models.token import RefreshToken


class TokenRepositoryInterface(ABC):
    """Интерфейс репозитория токенов"""

    @abstractmethod
    async def create(self, token_data: dict) -> RefreshToken:
        """Создание нового токена"""
        pass

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Получение токена по строке"""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[RefreshToken]:
        """Получение всех токенов пользователя"""
        pass

    @abstractmethod
    async def revoke_by_token(self, token: str) -> bool:
        """Отзыв токена"""
        pass

    @abstractmethod
    async def revoke_by_user_id(self, user_id: int) -> int:
        """Отзыв всех токенов пользователя"""
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Очистка истекших токенов"""
        pass
