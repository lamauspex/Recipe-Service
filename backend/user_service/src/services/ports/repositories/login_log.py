""" Интерфейс репозитория для логирования входов """

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID


class LoginLogRepositoryInterface(ABC):
    """Интерфейс репозитория для логирования входов"""

    @abstractmethod
    async def log_login_attempt(
        self,
        email: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        success: bool = False,
        failure_reason: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Логирование попытки входа"""
        pass

    @abstractmethod
    async def get_login_history(
        self,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Получение истории входов"""
        pass

    @abstractmethod
    async def get_failed_login_attempts(
        self,
        days: int = 1,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Получение неудачных попыток входа"""
        pass

    @abstractmethod
    async def get_login_statistics(
        self,
        days: int = 7
    ) -> Dict[str, Any]:
        """Получение статистики входов"""
        pass

    @abstractmethod
    async def get_suspicious_activity(
        self,
        days: int = 1,
        threshold: int = 5
    ) -> List[Dict[str, Any]]:
        """Получение подозрительной активности"""
        pass
