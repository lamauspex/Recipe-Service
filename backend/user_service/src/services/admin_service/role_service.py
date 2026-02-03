"""
Сервис для управления ролями и разрешениями
Продакшен-стандарт
"""

from typing import Optional
from sqlalchemy.orm import Session

from backend.user_service.src.models import RoleModel, Permission, DEFAULT_ROLES, User
from backend.user_service.src.exceptions.convenience import ServiceException


class RoleService:
    """Сервис для работы с ролями"""

    def __init__(self, db: Session):
        self.db = db

    # === CRUD OPERATIONS ===
    def get_role_by_id(self, role_id: str) -> Optional[RoleModel]:
        """Получить роль по ID"""

        return self.db.query(RoleModel).filter(
            RoleModel.id == role_id).first()

    def get_role_by_name(self, name: str) -> Optional[RoleModel]:
        """Получить роль по имени"""

        return self.db.query(RoleModel).filter(
            RoleModel.name == name).first()

    def get_all_roles(self) -> list[RoleModel]:
        """Получить все активные роли"""

        return self.db.query(RoleModel).filter(
            RoleModel.is_active is True).all()

    def create_role(
        self,
        name: str,
        display_name: str,
        permissions: int,
        description: Optional[str] = None,
        is_system: bool = False
    ) -> RoleModel:
        """Создать новую роль"""

        if self.get_role_by_name(name):
            raise ServiceException(f"Роль '{name}' уже существует")

        role = RoleModel(
            name=name,
            display_name=display_name,
            permissions=permissions,
            description=description,
            is_system=is_system
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(
        self,
        role_id: str,
        display_name: Optional[str] = None,
        permissions: Optional[int] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> RoleModel:
        """Обновить роль"""

        role = self.get_role_by_id(role_id)
        if not role:
            raise ServiceException(f"Роль с ID {role_id} не найдена")

        if role.is_system:
            raise ServiceException("Нельзя изменить системную роль")

        if display_name is not None:
            role.display_name = display_name
        if permissions is not None:
            role.permissions = permissions
        if description is not None:
            role.description = description
        if is_active is not None:
            role.is_active = is_active

        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role_id: str) -> bool:
        """Удалить роль (только не системные)"""

        role = self.get_role_by_id(role_id)
        if not role:
            raise ServiceException(f"Роль с ID {role_id} не найдена")

        if role.is_system:
            raise ServiceException("Нельзя удалить системную роль")

        self.db.delete(role)
        self.db.commit()
        return True

    # === PERMISSION HELPERS ===
    def add_permission_to_role(
        self,
        role_id: str,
        permission: Permission
    ) -> RoleModel:
        """Добавить разрешение к роли"""

        role = self.get_role_by_id(role_id)
        if not role:
            raise ServiceException(f"Роль с ID {role_id} не найдена")

        role.add_permission(permission)
        self.db.commit()
        self.db.refresh(role)
        return role

    def remove_permission_from_role(
        self,
        role_id: str,
        permission: Permission
    ) -> RoleModel:
        """Убрать разрешение у роли"""

        role = self.get_role_by_id(role_id)
        if not role:
            raise ServiceException(f"Роль с ID {role_id} не найдена")

        role.remove_permission(permission)
        self.db.commit()
        self.db.refresh(role)
        return role

    # === USER-ROLE MANAGEMENT ===
    def assign_role_to_user(self, user: User, role_name: str) -> User:
        """Назначить роль пользователю"""

        role = self.get_role_by_name(role_name)
        if not role:
            raise ServiceException(f"Роль '{role_name}' не найдена")

        user.add_role(role)
        self.db.commit()
        return user

    def remove_role_from_user(self, user: User, role_name: str) -> User:
        """Убрать роль у пользователя"""

        role = self.get_role_by_name(role_name)
        if not role:
            raise ServiceException(f"Роль '{role_name}' не найдена")

        user.remove_role(role)
        self.db.commit()
        return user

    def get_user_roles(self, user: User) -> list[RoleModel]:
        """Получить все роли пользователя"""

        return user.roles

    def get_user_permissions(self, user: User) -> list[Permission]:
        """Получить все разрешения пользователя (из всех ролей)"""

        permissions = []
        seen = set()
        for role in user.roles:
            for perm in role.permissions_list:
                if perm.value not in seen:
                    seen.add(perm.value)
                    permissions.append(perm)
        return permissions

    def user_has_permission(self, user: User, permission: Permission) -> bool:
        """Проверить есть ли у пользователя разрешение"""

        return user.has_permission(permission)

    def user_has_role(self, user: User, role_name: str) -> bool:
        """Проверить есть ли у пользователя роль"""

        return user.has_role(role_name)

    # === INITIALIZATION ===
    def ensure_default_roles(self) -> None:
        """Создать базовые роли если их нет"""

        for role_name, role_data in DEFAULT_ROLES.items():
            if not self.get_role_by_name(role_name):
                self.create_role(
                    name=role_name,
                    display_name=role_data["display_name"],
                    permissions=role_data["permissions"],
                    description=role_data["description"],
                    is_system=role_data["is_system"]
                )
