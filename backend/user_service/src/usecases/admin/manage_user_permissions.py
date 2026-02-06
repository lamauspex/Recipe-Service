"""
Usecase для управления разрешениями пользователя
"""

from typing import List
from uuid import UUID

from ...schemas.requests import UserPermissionsRequestDTO
from ...schemas.responses import UserPermissionsResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException
from ....models.user_models import User
from ....models.role_model import Permission, RoleModel
from ...infrastructure.repositories.user_repository import UserRepository
from ...infrastructure.repositories.role_repository import RoleRepository


class ManageUserPermissionsUsecase(BaseUsecase):
    """Usecase для управления разрешениями пользователя"""

    def __init__(self, user_repository: UserRepository, role_repository: RoleRepository, **kwargs):
        self.user_repository = user_repository
        self.role_repository = role_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: UserPermissionsRequestDTO
    ) -> UserPermissionsResponseDTO:
        """Выполнение управления разрешениями пользователя"""
        try:
            # Валидация UUID
            try:
                user_id = UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Получение пользователя
            user = await self.user_repository.get_by_id(str(user_id))
            if not user:
                raise NotFoundException("User not found")

            # Валидация разрешений
            permissions_mask = self._validate_permissions(request.permissions)

            # Создание временной роли с нужными разрешениями
            temp_role_name = f"temp_user_permissions_{user_id}"

            # Удаляем существующую временную роль если есть
            await self._cleanup_temp_roles(user)

            # Создаем новую временную роль
            temp_role_data = {
                "name": temp_role_name,
                "display_name": f"User {user_id} Permissions",
                "description": "Temporary role for user permissions",
                "permissions": permissions_mask,
                "is_active": True,
                "is_system": False
            }

            temp_role = await self.role_repository.create(temp_role_data)

            # Добавляем роль пользователю
            user.add_role(temp_role)
            await self.user_repository.update(str(user_id), {"roles": user.roles})

            # Возврат результата
            return UserPermissionsResponseDTO.create_success(
                user_id=str(user_id),
                permissions=request.permissions
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(
                f"Failed to manage user permissions: {str(e)}")

    def _validate_permissions(self, permissions: List[str]) -> int:
        """Валидация и преобразование разрешений в битовую маску"""
        if not permissions:
            return Permission.NONE

        permissions_mask = Permission.NONE
        for perm_name in permissions:
            if hasattr(Permission, perm_name.upper()):
                permissions_mask |= getattr(Permission, perm_name.upper())
            else:
                raise ValidationException(f"Invalid permission: {perm_name}")

        return permissions_mask

    async def _cleanup_temp_roles(self, user: User):
        """Очистка временных ролей пользователя"""
        temp_roles = [role for role in user.roles if role.name.startswith(
            "temp_user_permissions_")]
        for temp_role in temp_roles:
            user.remove_role(temp_role)
            await self.role_repository.delete(temp_role.id)

        if temp_roles:
            await self.user_repository.update(str(user.id), {"roles": user.roles})
