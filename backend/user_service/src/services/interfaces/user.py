"""
Интерфейсы для сервисов управления пользователями
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from ..dto.requests import (
    UserCreateRequestDTO, 
    UserUpdateRequestDTO, 
    UserChangePasswordRequestDTO
)
from ..dto.responses import (
    UserResponseDTO, 
    UserListResponseDTO, 
    UserCreateResponseDTO,
    UserUpdateResponseDTO,
    UserDeleteResponseDTO
)


class UserInterface(ABC):
    """Интерфейс сервиса управления пользователями"""
    
    @abstractmethod
    async def get_users(
        self, 
        page: int = 1, 
        per_page: int = 10,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> UserListResponseDTO:
        """Получение списка пользователей с пагинацией и фильтрацией"""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserResponseDTO:
        """Получение пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserResponseDTO]:
        """Получение пользователя по email"""
        pass
    
    @abstractmethod
    async def create_user(self, request: UserCreateRequestDTO) -> UserCreateResponseDTO:
        """Создание нового пользователя"""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: int, request: UserUpdateRequestDTO) -> UserUpdateResponseDTO:
        """Обновление данных пользователя"""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: int) -> UserDeleteResponseDTO:
        """Удаление пользователя"""
        pass
    
    @abstractmethod
    async def change_password(self, user_id: int, request: UserChangePasswordRequestDTO) -> UserUpdateResponseDTO:
        """Смена пароля пользователя"""
        pass
    
    @abstractmethod
    async def activate_user(self, user_id: int) -> UserUpdateResponseDTO:
        """Активация пользователя"""
        pass
    
    @abstractmethod
    async def deactivate_user(self, user_id: int) -> UserUpdateResponseDTO:
        """Деактивация пользователя"""
        pass
    
    @abstractmethod
    async def verify_user(self, user_id: int) -> UserUpdateResponseDTO:
        """Верификация пользователя"""
        pass