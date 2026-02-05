"""
Сервис для управления ролями и разрешениями
Продакшен-стандарт
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from backend.user_service.src.models import RoleModel, Permission, DEFAULT_ROLES, User
from backend.user_service.src.exceptions.convenience import ServiceException
from backend.user_service.src.schemas import RoleResponse, RoleCreate, RoleUpdate


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

    def get_all_roles(self) -> List[RoleModel]:
        """Получить все активные роли"""

        return self.db.query(RoleModel).filter(
            RoleModel.is_active is True).all()

    def create_role_response(self, role_data: RoleCreate) -> dict:
        """Создать новую роль - возвращает готовый ответ"""

        try:
            if self.get_role_by_name(role_data.name):
                raise ServiceException(
                    f"Роль '{role_data.name}' уже существует")

            role = RoleModel(
                name=role_data.name,
                display_name=role_data.display_name,
                permissions=role_data.permissions,
                description=role_data.description,
                is_system=False
            )
            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)

            return {
                "role": RoleResponse.model_validate(role),
                "message": "Роль успешно создана",
                "success": True
            }

        except ServiceException:
            raise
        except Exception as e:
            return {
                "error": f"Ошибка при создании роли: {str(e)}",
                "success": False
            }

    def get_all_roles_response(self) -> dict:
        """Получить все роли - возвращает готовый ответ"""

        try:
            roles = self.get_all_roles()
            role_responses = [
                RoleResponse.model_validate(role) for role in roles]

            return {
                "roles": role_responses,
                "total_count": len(role_responses),
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Ошибка при получении ролей: {str(e)}",
                "success": False
            }

    def get_role_by_id_response(self, role_id: str) -> dict:
        """Получить роль по ID - возвращает готовый ответ"""

        try:
            role = self.get_role_by_id(role_id)
            if not role:
                return {
                    "error": f"Роль с ID {role_id} не найдена",
                    "success": False
                }

            return {
                "role": RoleResponse.model_validate(role),
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Ошибка при получении роли: {str(e)}",
                "success": False
            }

    def update_role_response(self, role_id: str, role_data: RoleUpdate) -> dict:
        """Обновить роль - возвращает готовый ответ"""

        try:
            role = self.get_role_by_id(role_id)
            if not role:
                return {
                    "error": f"Роль с ID {role_id} не найдена",
                    "success": False
                }

            if role.is_system:
                return {
                    "error": "Нельзя изменить системную роль",
                    "success": False
                }

            # Обновляем поля
            update_data = role_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(role, key):
                    setattr(role, key, value)

            self.db.commit()
            self.db.refresh(role)

            return {
                "role": RoleResponse.model_validate(role),
                "message": "Роль успешно обновлена",
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Ошибка при обновлении роли: {str(e)}",
                "success": False
            }

    def delete_role_response(self, role_id: str) -> dict:
        """Удалить роль - возвращает готовый ответ"""

        try:
            role = self.get_role_by_id(role_id)
            if not role:
                return {
                    "error": f"Роль с ID {role_id} не найдена",
                    "success": False
                }

            if role.is_system:
                return {
                    "error": "Нельзя удалить системную роль",
                    "success": False
                }

            self.db.delete(role)
            self.db.commit()

            return {
                "message": "Роль успешно удалена",
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Ошибка при удалении роли: {str(e)}",
                "success": False
            }

    # === USER-ROLE MANAGEMENT ===
    def get_user_permissions_response(self, user_id: str) -> dict:
        """Получить разрешения пользователя - возвращает готовый ответ"""

        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {
                    "error": f"Пользователь с ID {user_id} не найден",
                    "success": False
                }

            permissions = self.get_user_permissions(user)
            permission_names = [p.name for p in permissions]

            return {
                "user_id": user_id,
                "permissions": permission_names,
                "total_count": len(permission_names),
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Ошибка при получении разрешений пользователя: {str(e)}",
                "success": False
            }

    def check_user_permission_response(self, user_id: str, permission: str) -> dict:
        """Проверить разрешение пользователя - возвращает готовый ответ"""

        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {
                    "error": f"Пользователь с ID {user_id} не найден",
                    "success": False
                }

            try:
                perm = Permission[permission.upper()]
            except KeyError:
                return {
                    "error": f"Разрешение '{permission}' не существует",
                    "success": False
                }

            has_perm = self.user_has_permission(user, perm)

            return {
                "user_id": user_id,
                "permission": permission,
                "has_permission": has_perm,
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Ошибка при проверке разрешения: {str(e)}",
                "success": False
            }

    def get_available_permissions_response(self) -> dict:
        """Получить список доступных разрешений - возвращает готовый ответ"""

        try:
            permissions = sorted(
                [p.name for p in Permission if p != Permission.NONE])

            return {
                "permissions": permissions,
                "total_count": len(permissions),
                "success": True
            }

        except Exception as e:
            return {
                "error": f"Ошибка при получении списка разрешений: {str(e)}",
                "success": False
            }

    # === LEGACY METHODS (оставляем для обратной совместимости) ===
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
