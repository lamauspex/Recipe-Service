"""
Сервис для работы с пользователями
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from backend.services.user_service.src.models import User
from backend.services.user_service.src.schemas import UserCreate, UserUpdate
from backend.services.user_service.src.repository.repo import UserRepository


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def create_user(self, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        from .auth_service import AuthService

        auth_service = AuthService(self.db)
        hashed_password = auth_service.get_password_hash(user_data.password)

        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name,
            "bio": user_data.bio
        }

        return self.repository.create_user(user_dict)

    def get_user(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.repository.get_user_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        return self.repository.get_user_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.repository.get_user_by_email(email)

    def update_user(self,
                    user_id: int,
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

    def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        return self.repository.delete_user(user_id)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей"""
        return self.repository.get_users(skip=skip, limit=limit)

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка активных пользователей"""
        return self.repository.get_active_users(skip=skip, limit=limit)

    def activate_user(self, user_id: int) -> Optional[User]:
        """Активация пользователя"""
        return self.repository.update_user(user_id, {"is_active": True})

    def deactivate_user(self, user_id: int) -> Optional[User]:
        """Деактивация пользователя"""
        return self.repository.update_user(user_id, {"is_active": False})

    def set_admin(self, user_id: int, is_admin: bool = True) -> Optional[User]:
        """Установка прав администратора"""
        return self.repository.update_user(user_id, {"is_admin": is_admin})
