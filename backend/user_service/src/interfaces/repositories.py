"""
Интерфейсы для репозиториев
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID


class UserRepositoryInterface(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[Any]:
        """Получение пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Any]:
        """Получение пользователя по email"""
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[Any]:
        """Получение пользователя по username"""
        pass
    
    @abstractmethod
    async def create(self, user_data: Dict[str, Any]) -> Any:
        """Создание пользователя"""
        pass
    
    @abstractmethod
    async def update(self, user_id: str, updates: Dict[str, Any]) -> Optional[Any]:
        """Обновление пользователя"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Удаление пользователя"""
        pass


class RoleRepositoryInterface(ABC):
    """Интерфейс репозитория ролей"""
    
    @abstractmethod
    async def get_by_id(self, role_id: str) -> Optional[Any]:
        """Получение роли по ID"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Any]:
        """Получение роли по имени"""
        pass
    
    @abstractmethod
    async def create(self, role_data: Dict[str, Any]) -> Any:
        """Создание роли"""
        pass
    
    @abstractmethod
    async def update(self, role_id: str, updates: Dict[str, Any]) -> Optional[Any]:
        """Обновление роли"""
        pass
    
    @abstractmethod
    async def delete(self, role_id: str) -> bool:
        """Удаление роли"""
        pass


class TokenRepositoryInterface(ABC):
    """Интерфейс репозитория токенов"""
    
    @abstractmethod
    async def create(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание токена"""
        pass
    
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Получение токена по значению"""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение токенов пользователя"""
        pass
    
    @abstractmethod
    async def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""
        pass


class AdminRepositoryInterface(ABC):
    """Интерфейс административного репозитория"""
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[Any]:
        """Получение пользователя по ID"""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Any]:
        """Обновление пользователя"""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Удаление пользователя"""
        pass


class UserRoleRepositoryInterface(ABC):
    """Интерфейс репозитория связей пользователь-роль"""
    
    @abstractmethod
    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Назначение роли пользователю"""
        pass
    
    @abstractmethod
    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Удаление роли у пользователя"""
        pass
    
    @abstractmethod
    async def get_user_roles(self, user_id: str) -> List[Any]:
        """Получение ролей пользователя"""
        pass
    
    @abstractmethod
    async def user_has_role(self, user_id: str, role_name: str) -> bool:
        """Проверка наличия роли у пользователя"""
        pass
