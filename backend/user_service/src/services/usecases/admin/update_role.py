"""
Usecase для обновления роли
"""

from typing import List
from uuid import UUID

from ...dto.requests import RoleUpdateRequestDTO
from ...dto.responses import RoleUpdateResponseDTO, RoleResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException, ConflictException
from ....models.role_model import RoleModel, Permission
from ...infrastructure.repositories.role_repository import RoleRepository


class UpdateRoleUsecase(BaseUsecase):
    """Usecase для обновления роли"""

    def __init__(self, role_repository: RoleRepository, **kwargs):
        self.role_repository = role_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: RoleUpdateRequestDTO
    ) -> RoleUpdateResponseDTO:
        """Выполнение обновления роли"""
        try:
            # Валидация UUID
            if not hasattr(request, 'role_id'):
                raise ValidationException("role_id is required")

            try:
                role_id = UUID(request.role_id)
            except ValueError:
                raise ValidationException("Invalid role ID format")

            # Получение роли
            role = await self.role_repository.get_by_id(str(role_id))
            if not role:
                raise NotFoundException(
                    f"Role with ID {request.role_id} not found")

            # Проверка системной роли (системные роли нельзя изменять)
            if role.is_system:
                raise ValidationException("Cannot update system role")

            # Подготовка данных для обновления
            update_data = {}

            if request.display_name is not None:
                update_data["display_name"] = request.display_name

            if request.description is not None:
                update_data["description"] = request.description

            if request.is_active is not None:
                update_data["is_active"] = request.is_active

            # Валидация разрешений если указаны
            if request.permissions is not None:
                permissions_mask = self._validate_permissions(
                    request.permissions)
                update_data["permissions"] = permissions_mask

            # Проверка уникальности имени роли если изменяется
            if "display_name" in update_data:
                existing_role = await self.role_repository.get_by_name(update_data["display_name"])
                if existing_role and str(existing_role.id) != str(role_id):
                    raise ConflictException(
                        f"Role with name '{update_data['display_name']}' already exists")

            # Обновление роли
            updated_role = await self.role_repository.update(str(role_id), update_data)
            if not updated_role:
                raise ValidationException("Failed to update role")

            # Возврат результата
            return RoleUpdateResponseDTO.create_success(
                role=self._serialize_role(updated_role)
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException, ConflictException)):
                raise e
            raise ValidationException(f"Failed to update role: {str(e)}")

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

    def _serialize_role(self, role: RoleModel) -> RoleResponseDTO:
        """Сериализация роли"""
        return RoleResponseDTO(
            id=str(role.id),
            name=role.name,
            display_name=role.display_name,
            description=role.description,
            permissions=role.permissions,
            permissions_list=[p.name for p in role.permissions_list],
            is_system=role.is_system,
            is_active=role.is_active,
            created_at=role.created_at.isoformat() if role.created_at else None,
            updated_at=role.updated_at.isoformat() if role.updated_at else None
        )
