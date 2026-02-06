"""
Интерфейсы репозиториев для работы с пользователями
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from backend.user_service.src.models.user_models import User


class UserRepositoryInterface(ABC):
    """Интерфейс репозитория пользователей"""

    @abstractmethod
    async def create(self, user_data: dict) -> User:
        """Создание нового пользователя"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        pass

    @abstractmethod
    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """Обновление данных пользователя"""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Удаление пользователя"""
        pass

    @abstractmethod
    async def get_list(
        self,
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """Получение списка пользователей с пагинацией и фильтрацией"""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Проверка существования пользователя с данным email"""
        pass

    @abstractmethod
    async def count_active_users(self) -> int:
        """Подсчет активных пользователей"""
        pass
