"""
Сервис для работы с пользователями
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from backend.services.user_service.src.repository.user_repo import (
    UserRepository)
from backend.services.user_service.src.repository.token_repo import (
    RefreshTokenRepository)
from backend.services.user_service.src.services.auth_service import (
    AuthService)
from backend.services.user_service.src.events.publishers import (
    user_event_publisher)
from backend.services.user_service.schemas.schemas import UserCreate
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для управления пользователями"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)
        self.auth_service = AuthService(db)

    def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """Создание нового пользователя"""
        # Проверяем, существует ли пользователь с таким email
        existing_user = self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("Пользователь с таким email уже существует")

        # Создаем пользователя с хешированным паролем
        user_dict = user_data.dict()
        hashed_password = self.auth_service.hash_password(
            user_dict.pop("password"))
        user_dict["hashed_password"] = hashed_password

        user = self.user_repo.create_user(user_dict)

        # Публикуем событие создания пользователя
        user_event_publisher.publish_user_created(user.id, user.email)

        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat()
        }

    def get_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Получение пользователя по ID"""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            return None

        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по email"""
        user = self.user_repo.get_user_by_email(email)
        if not user:
            return None

        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Получение пользователя по username"""
        user = self.user_repo.get_user_by_username(username)
        if not user:
            return None

        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }

    def update_user(self, user_id: UUID, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновление данных пользователя"""
        user = self.user_repo.update_user(user_id, user_data)
        if not user:
            return None

        # Публикуем событие обновления пользователя
        user_event_publisher.publish_user_updated(user.id, user.email)

        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "updated_at": user.updated_at.isoformat()
        }

    def delete_user(self, user_id: UUID) -> bool:
        """Удаление пользователя"""
        # Отзываем все токены пользователя
        self.token_repo.revoke_user_tokens(user_id)

        # Удаляем пользователя
        result = self.user_repo.delete_user(user_id)

        if result:
            # Публикуем событие удаления пользователя
            user_event_publisher.publish_user_deleted(user_id)

        return result

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Аутентификация пользователя"""
        user = self.auth_service.authenticate(email, password)
        if not user:
            return None

        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Обновление access токена"""
        token = self.token_repo.get_valid_token(refresh_token)
        if not token:
            return None

        user = self.user_repo.get_user_by_id(token.user_id)
        if not user:
            return None

        # Генерируем новую пару токенов
        tokens = self.auth_service.generate_tokens(user)

        # Создаем новый refresh токен
        self.token_repo.create_refresh_token(
            user_id=user.id,
            token=tokens["refresh_token"],
            expires_at=tokens["refresh_expires_at"]
        )

        return tokens

    def logout(self, refresh_token: str) -> bool:
        """Выход пользователя"""
        return self.token_repo.revoke_token(refresh_token)

    def get_users_list(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение списка пользователей"""
        users = self.user_repo.get_users(skip=skip, limit=limit)

        return [
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at.isoformat()
            }
            for user in users
        ]

    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Изменение пароля пользователя"""
        # Проверяем текущий пароль
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            return False

        if not self.auth_service.verify_password(current_password, user.hashed_password):
            return False

        # Хешируем новый пароль
        hashed_new_password = self.auth_service.hash_password(new_password)

        # Обновляем пароль
        updated_user = self.user_repo.update_password(
            user_id, hashed_new_password)
        if not updated_user:
            return False

        # Отзываем все токены пользователя
        self.token_repo.revoke_user_tokens(user_id)

        # Публикуем событие изменения пароля
        user_event_publisher.publish_user_password_changed(user_id, user.email)

        return True

    def revoke_all_user_tokens(self, user_id: UUID) -> bool:
        """Отзыв всех токенов пользователя"""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            return False

        self.token_repo.revoke_user_tokens(user_id)
        return True

    def activate_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Активация пользователя"""
        user = self.user_repo.activate_user(user_id)
        if not user:
            return None

        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active
        }

    def deactivate_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Деактивация пользователя"""
        user = self.user_repo.deactivate_user(user_id)
        if not user:
            return None

        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active
        }

    def set_admin(self, user_id: UUID, is_admin: bool = True) -> Optional[Dict[str, Any]]:
        """Установка статуса администратора"""
        user = self.user_repo.set_admin(user_id, is_admin)
        if not user:
            return None

        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin
        }

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение списка активных пользователей"""
        users = self.user_repo.get_active_users(skip=skip, limit=limit)

        return [
            {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            }
            for user in users
        ]
