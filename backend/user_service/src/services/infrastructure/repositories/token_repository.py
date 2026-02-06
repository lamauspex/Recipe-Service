"""
Адаптер для работы с репозиторием токенов
"""
from typing import List, Optional
from ...models.models import RefreshToken
from ...ports.repositories.token import TokenRepositoryInterface


class TokenRepositoryAdapter(TokenRepositoryInterface):
    """Адаптер для работы с репозиторием токенов"""

    def __init__(self, db_session):
        self.db_session = db_session

    async def create(self, token_data: dict) -> RefreshToken:
        """Создание нового токена"""

        # Здесь будет реальная логика работы с базой данных
        # Пока возвращаем заглушку
        token = RefreshToken(**token_data)
        # await self.db_session.add(token)
        # await self.db_session.commit()
        # await self.db_session.refresh(token)
        return token

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Получение токена по строке"""
        # Здесь будет реальная логика работы с базой данных
        # Пока возвращаем заглушку
        return None

    async def get_by_user_id(self, user_id: int) -> List[RefreshToken]:
        """Получение всех токенов пользователя"""
        # Здесь будет реальная логика работы с базой данных
        # Пока возвращаем заглушку
        return []

    async def revoke_by_token(self, token: str) -> bool:
        """Отзыв токена"""
        # Здесь будет реальная логика работы с базой данных
        # Пока возвращаем заглушку
        return False

    async def revoke_by_user_id(self, user_id: int) -> int:
        """Отзыв всех токенов пользователя"""
        # Здесь будет реальная логика работы с базой данных
        # Пока возвращаем заглушку
        return 0

    async def cleanup_expired(self) -> int:
        """Очистка истекших токенов"""
        # Здесь будет реальная логика работы с базой данных
        # Пока возвращаем заглушку
        return 0
