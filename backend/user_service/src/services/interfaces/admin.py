"""
Интерфейсы для административных сервисов
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..dto.responses import UserResponseDTO


class AdminInterface(ABC):
    """Интерфейс административного сервиса"""
    
    @abstractmethod
    async def get_user_statistics(self) -> dict:
        """Получение статистики пользователей"""
        pass
    
    @abstractmethod
    async def bulk_activate_users(self, user_ids: List[int]) -> dict:
        """Массовая активация пользователей"""
        pass
    
    @abstractmethod
    async def bulk_deactivate_users(self, user_ids: List[int]) -> dict:
        """Массовая деактивация пользователей"""
        pass
    
    @abstractmethod
    async def bulk_delete_users(self, user_ids: List[int]) -> dict:
        """Массовое удаление пользователей"""
        pass
    
    @abstractmethod
    async def export_users(self, format: str = "csv") -> bytes:
        """Экспорт пользователей"""
        pass
    
    @abstractmethod
    async def get_system_health(self) -> dict:
        """Получение состояния системы"""
        pass