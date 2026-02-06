"""
Сервис для работы с ролями и разрешениями
Разделен на отдельные сервисы для лучшей архитектуры
"""

from typing import Dict, Any, List
from uuid import UUID

from backend.user_service.src.models import User, RoleModel
from backend.user_service.src.exceptions.base import NotFoundException, ConflictException
from common.base_service import BaseService
from common.response_builder import ResponseBuilder


class RoleService(BaseService):
    """Сервис для управления ролями"""

    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session

    def create_role(self, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание новой роли"""
        try:
            # Проверяем, существует ли роль с таким именем
            existing_role = self.db_session.query(RoleModel).filter(
                RoleModel.name == role_data["name"]
            ).first()

            if existing_role:
                return ResponseBuilder.error(
                    "Роль с таким именем уже существует",
                    error_code="ROLE_EXISTS"
                )

            # Создаем новую роль
            new_role = RoleModel(
                name=role_data["name"],
                description=role_data.get("description", ""),
                permissions=role_data.get("permissions", [])
            )

            self.db_session.add(new_role)
            self.db_session.commit()

            return self._handle_success(
                "Роль создана",
                data=self._serialize_role(new_role)
            )

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "создания роли")

    def get_role(self, role_id: UUID) -> Dict[str, Any]:
        """Получение роли по ID"""
        try:
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not role:
                return ResponseBuilder.not_found("Роль")

            return self._handle_success(
                "Роль найдена",
                data=self._serialize_role(role)
            )

        except Exception as e:
            return self._handle_error(e, "получения роли")

    def list_roles(self) -> Dict[str, Any]:
        """Получение списка всех ролей"""
        try:
            roles = self.db_session.query(RoleModel).all()

            return self._handle_success(
                "Список ролей получен",
                data={
                    "roles": [self._serialize_role(role) for role in roles],
                    "total": len(roles)
                }
            )

        except Exception as e:
            return self._handle_error(e, "получения списка ролей")

    def update_role(self, role_id: UUID, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление роли"""
        try:
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not role:
                return ResponseBuilder.not_found("Роль")

            # Проверяем уникальность имени роли
            if "name" in update_data:
                existing_role = self.db_session.query(RoleModel).filter(
                    RoleModel.name == update_data["name"]
                ).first()

                if existing_role and existing_role.id != role_id:
                    return ResponseBuilder.error(
                        "Роль с таким именем уже существует",
                        error_code="ROLE_EXISTS"
                    )

            # Обновляем поля
            for field, value in update_data.items():
                if hasattr(role, field):
                    setattr(role, field, value)

            self.db_session.commit()

            return self._handle_success(
                "Роль обновлена",
                data=self._serialize_role(role)
            )

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "обновления роли")

    def delete_role(self, role_id: UUID) -> Dict[str, Any]:
        """Удаление роли"""
        try:
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not role:
                return ResponseBuilder.not_found("Роль")

            # Проверяем, есть ли пользователи с этой ролью
            users_with_role = self.db_session.query(User).filter(
                User.roles.any(RoleModel.id == role_id)
            ).count()

            if users_with_role > 0:
                return ResponseBuilder.error(
                    "Нельзя удалить роль, которая назначена пользователям",
                    error_code="ROLE_IN_USE"
                )

            self.db_session.delete(role)
            self.db_session.commit()

            return self._handle_success("Роль удалена")

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "удаления роли")

    def _serialize_role(self, role: RoleModel) -> Dict[str, Any]:
        """Сериализация роли для ответа API"""
        return {
            "id": str(role.id),
            "name": role.name,
            "description": role.description,
            "permissions": role.permissions,
            "created_at": role.created_at.isoformat(),
            "updated_at": role.updated_at.isoformat()
        }


class UserRoleService(BaseService):
    """Сервис для управления ролями пользователей"""

    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session

    def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> Dict[str, Any]:
        """Назначение роли пользователю"""
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            if not role:
                return ResponseBuilder.not_found("Роль")

            # Проверяем, есть ли уже эта роль у пользователя
            if role in user.roles:
                return ResponseBuilder.error(
                    "У пользователя уже есть эта роль",
                    error_code="ROLE_ALREADY_ASSIGNED"
                )

            user.add_role(role)
            self.db_session.commit()

            return self._handle_success(
                f"Роль {role.name} назначена пользователю"
            )

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "назначения роли")

    def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> Dict[str, Any]:
        """Удаление роли у пользователя"""
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            if not role:
                return ResponseBuilder.not_found("Роль")

            if role not in user.roles:
                return ResponseBuilder.error(
                    "У пользователя нет этой роли",
                    error_code="ROLE_NOT_ASSIGNED"
                )

            user.remove_role(role)
            self.db_session.commit()

            return self._handle_success(
                f"Роль {role.name} удалена у пользователя"
            )

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "удаления роли")

    def get_user_roles(self, user_id: UUID) -> Dict[str, Any]:
        """Получение ролей пользователя"""
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            roles = [self._serialize_role(role) for role in user.roles]

            return self._handle_success(
                "Роли пользователя получены",
                data={
                    "user_id": str(user_id),
                    "roles": roles,
                    "total": len(roles)
                }
            )

        except Exception as e:
            return self._handle_error(e, "получения ролей пользователя")

    def _serialize_role(self, role: RoleModel) -> Dict[str, Any]:
        """Сериализация роли для ответа API"""
        return {
            "id": str(role.id),
            "name": role.name,
            "description": role.description,
            "permissions": role.permissions
        }


class PermissionService(BaseService):
    """Сервис для проверки разрешений"""

    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session

    def check_user_permission(self, user_id: UUID, permission: str) -> Dict[str, Any]:
        """Проверка разрешения пользователя"""
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            has_permission = self._user_has_permission(user, permission)

            return self._handle_success(
                "Проверка разрешения выполнена",
                data={
                    "user_id": str(user_id),
                    "permission": permission,
                    "has_permission": has_permission
                }
            )

        except Exception as e:
            return self._handle_error(e, "проверки разрешения")

    def _user_has_permission(self, user: User, permission: str) -> bool:
        """Проверка, есть ли у пользователя определенное разрешение"""
        for role in user.roles:
            if permission in role.permissions:
                return True
        return False
