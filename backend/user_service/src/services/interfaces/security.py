"""
Интерфейсы для сервисов безопасности
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..dto.responses import UserResponseDTO


class SecurityInterface(ABC):
    """Интерфейс сервиса безопасности"""
    
    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        pass
    
    @abstractmethod
    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        pass
    
    @abstractmethod
    async def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        """Генерация access токена"""
        pass
    
    @abstractmethod
    async def generate_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Генерация refresh токена"""
        pass
    
    @abstractmethod
    async def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка access токена"""
        pass
    
    @abstractmethod
    async def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка refresh токена"""
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""
        pass
    
    @abstractmethod
    async def generate_password_reset_token(self, user_email: str) -> str:
        """Генерация токена для сброса пароля"""
        pass
    
    @abstractmethod
    async def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Проверка токена для сброса пароля"""
        pass