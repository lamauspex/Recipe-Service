"""
Сервис для работы с пользователями
"""
from typing import Optional, List
from uuid import UUID

from backend.services.user_service.src.repository.user_repo import (
    UserRepository)
from backend.services.user_service.src.services.auth_service import AuthService
from backend.services.user_service.models.user_models import User
from backend.services.user_service.schemas.schemas import (
    UserCreate, UserUpdate)


class UserService:
    """Сервис для управления пользователями"""

    def __init__(self, db_session):
        self.repository = UserRepository(db_session)

    def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        # Проверяем существование пользователя
        if self.repository.get_user_by_username(user_data.user_name):
            raise ValueError("Пользователь с таким user_name уже существует")

        if self.repository.get_user_by_email(user_data.email):
            raise ValueError("Пользователь с таким email уже существует")

        # Хэшируем пароль
        auth_service = AuthService(self.repository.db)
        hashed_password = auth_service.get_password_hash(user_data.password)

        user_dict = {
            "user_name": user_data.user_name,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name
        }

        return self.repository.create_user(user_dict)

    def get_user(self, user_id: UUID) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.repository.get_user_by_id(user_id)

    def get_user_by_username(self, user_name: str) -> Optional[User]:
        """Получение пользователя по user_name"""
        return self.repository.get_user_by_username(user_name)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.repository.get_user_by_email(email)

    def update_user(self,
                    user_id: UUID,
                    user_data: UserUpdate
                    ) -> Optional[User]:
        """Обновление данных пользователя"""
        # Если user_data это уже dict, используем его напрямую
        if isinstance(user_data, dict):
            update_data = user_data
        else:
            # Используем правильный метод для Pydantic v2
            if hasattr(user_data, 'model_dump'):
                update_data = user_data.model_dump(exclude_unset=True)
            else:
                # Fallback для старых версий
                update_data = user_data.dict(exclude_unset=True)

        # Валидация email при обновлении
        if "email" in update_data:
            existing_user = self.get_user_by_email(update_data["email"])
            if existing_user and existing_user.id != user_id:
                raise ValueError("Пользователь с таким email уже существует")

        return self.repository.update_user(user_id, update_data)

    def delete_user(self, user_id: UUID) -> bool:
        """Удаление пользователя"""
        return self.repository.delete_user(user_id)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей"""
        return self.repository.get_users(skip=skip, limit=limit)

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка активных пользователей"""
        return self.repository.get_active_users(skip=skip, limit=limit)

    def activate_user(self, user_id: UUID) -> Optional[User]:
        """Активация пользователя"""
        return self.repository.update_user(user_id, {"is_active": True})

    def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Деактивация пользователя"""
        return self.repository.update_user(user_id, {"is_active": False})

    def set_admin(self,
                  user_id: UUID,
                  is_admin: bool = True
                  ) -> Optional[User]:
        """Установка прав администратора"""
        return self.repository.update_user(user_id, {"is_admin": is_admin})
