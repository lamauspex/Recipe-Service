"""
Сервис для работы с пользователями
Обновлен для использования базового класса и утилиты паролей
"""

from datetime import datetime, timezone
from uuid import UUID
from typing import Optional, Dict, Any, List

from backend.user_service.src.models import User, RoleModel
from backend.user_service.src.repository import UserRepository
from backend.user_service.src.exceptions.base import (
    NotFoundException,
    ConflictException,
    UnauthorizedException
)
from common.base_service import BaseService
from common.response_builder import ResponseBuilder
from common.password_utility import password_utility


class UserService(BaseService):
    """Сервис для работы с пользователями"""

    def __init__(self, db_session):
        super().__init__()
        self.repo = UserRepository(db_session)

    def get_user_by_id(self, user_id: UUID) -> Dict[str, Any]:
        """Получение пользователя по ID"""
        try:
            user = self.repo.get_user_by_id(user_id)
            if not user:
                return ResponseBuilder.not_found("Пользователь")

            return self._handle_success(
                "Пользователь найден",
                data=self._serialize_user(user)
            )

        except Exception as e:
            return self._handle_error(e, "получения пользователя по ID")

    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Получение пользователя по email"""
        try:
            user = self.repo.get_user_by_email(email)
            if not user:
                return ResponseBuilder.not_found("Пользователь")

            return self._handle_success(
                "Пользователь найден",
                data=self._serialize_user(user)
            )

        except Exception as e:
            return self._handle_error(e, "получения пользователя по email")

    def get_user_by_user_name(self, user_name: str) -> Dict[str, Any]:
        """Получение пользователя по имени пользователя"""
        try:
            user = self.repo.get_user_by_user_name(user_name)
            if not user:
                return ResponseBuilder.not_found("Пользователь")

            return self._handle_success(
                "Пользователь найден",
                data=self._serialize_user(user)
            )

        except Exception as e:
            return self._handle_error(e, "получения пользователя по имени")

    def update_user(self, user_id: UUID, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление пользователя"""
        try:
            # Проверяем существование пользователя
            user = self.repo.get_user_by_id(user_id)
            if not user:
                return ResponseBuilder.not_found("Пользователь")

            # Проверяем уникальность email, если он обновляется
            if "email" in update_data:
                existing_user = self.repo.get_user_by_email(
                    update_data["email"])
                if existing_user and existing_user.id != user_id:
                    return ResponseBuilder.error(
                        "Пользователь с таким email уже существует",
                        error_code="EMAIL_EXISTS"
                    )

            # Проверяем уникальность username, если он обновляется
            if "user_name" in update_data:
                existing_user = self.repo.get_user_by_user_name(
                    update_data["user_name"])
                if existing_user and existing_user.id != user_id:
                    return ResponseBuilder.error(
                        "Пользователь с таким именем уже существует",
                        error_code="USERNAME_EXISTS"
                    )

            # Обновляем пароль, если он передан
            if "password" in update_data:
                update_data["hashed_password"] = password_utility.hash_password(
                    update_data.pop("password"))

            # Обновляем время изменения
            update_data["updated_at"] = datetime.now(timezone.utc)

            # Обновляем пользователя
            updated_user = self.repo.update_user(user_id, update_data)

            return self._handle_success(
                "Пользователь обновлен",
                data=self._serialize_user(updated_user)
            )

        except Exception as e:
            return self._handle_error(e, "обновления пользователя")

    def delete_user(self, user_id: UUID) -> Dict[str, Any]:
        """Удаление пользователя"""
        try:
            # Проверяем существование пользователя
            user = self.repo.get_user_by_id(user_id)
            if not user:
                return ResponseBuilder.not_found("Пользователь")

            # Мягкое удаление - деактивация
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)

            return self._handle_success("Пользователь деактивирован")

        except Exception as e:
            return self._handle_error(e, "удаления пользователя")

    def list_users(
        self,
        page: int = 1,
        per_page: int = 10,
        search: str = None,
        is_active: bool = None
    ) -> Dict[str, Any]:
        """Получение списка пользователей с пагинацией и фильтрацией"""
        try:
            # Здесь должна быть логика получения пользователей с фильтрацией
            # Пока что возвращаем базовый ответ
            return self._handle_success(
                "Список пользователей получен",
                data={"users": [], "total": 0,
                      "page": page, "per_page": per_page}
            )

        except Exception as e:
            return self._handle_error(e, "получения списка пользователей")

    def activate_user(self, user_id: UUID) -> Dict[str, Any]:
        """Активация пользователя"""
        try:
            user = self.repo.get_user_by_id(user_id)
            if not user:
                return ResponseBuilder.not_found("Пользователь")

            user.is_active = True
            user.updated_at = datetime.now(timezone.utc)

            return self._handle_success("Пользователь активирован")

        except Exception as e:
            return self._handle_error(e, "активации пользователя")

    def deactivate_user(self, user_id: UUID) -> Dict[str, Any]:
        """Деактивация пользователя"""
        try:
            user = self.repo.get_user_by_id(user_id)
            if not user:
                return ResponseBuilder.not_found("Пользователь")

            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)

            return self._handle_success("Пользователь деактивирован")

        except Exception as e:
            return self._handle_error(e, "деактивации пользователя")

    def _serialize_user(self, user: User) -> Dict[str, Any]:
        """Сериализация пользователя для ответа API"""
        return {
            "id": str(user.id),
            "user_name": user.user_name,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "is_locked": user.is_locked,
            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
