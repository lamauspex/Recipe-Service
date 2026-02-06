"""
Usecase для создания роли
"""

from typing import List

from ...schemas.requests import RoleCreateRequestDTO
from ...schemas.responses import RoleCreateResponseDTO, RoleResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ConflictException, ValidationException
from ...infrastructure.repositories.role_repository import RoleRepository


# Заглушки для моделей
class Permission:
    """Заглушка для Permission"""
    NONE = 0


class CreateRoleUsecase(BaseUsecase):
    """Usecase для создания роли"""

    def __init__(self, role_repository: RoleRepository, **kwargs):
        self.role_repository = role_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: RoleCreateRequestDTO
    ) -> RoleCreateResponseDTO:
        """Выполнение создания роли"""
        try:
            # Проверка уникальности имени роли
            existing_role = await self.role_repository.get_by_name(request.name)
            if existing_role:
                raise ConflictException(
                    f"Role with name '{request.name}' already exists")

            # Валидация разрешений
            permissions_mask = self._validate_permissions(request.permissions)

            # Создание роли
            role_data = {
                "name": request.name,
                "display_name": request.display_name,
                "description": request.description,
                "permissions": permissions_mask,
                "is_active": request.is_active,
                "is_system": False
            }

            role = await self.role_repository.create(role_data)

            # Возврат результата
            return RoleCreateResponseDTO.create_success(
                role=self._serialize_role(role)
            )

        except Exception as e:
            if isinstance(e, (ConflictException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to create role: {str(e)}")

    def _validate_permissions(self, permissions: List[str]) -> int:
        """Валидация и преобразование разрешений в битовую маску"""
        if not permissions:
            return Permission.NONE

        permissions_mask = Permission.NONE
        for perm_name in permissions:
            # Заглушка - в реальной реализации здесь была бы проверка доступных разрешений
            if perm_name.lower() in ['read', 'write', 'delete', 'admin']:
                permissions_mask |= 1  # Простая заглушка
            else:
                raise ValidationException(f"Invalid permission: {perm_name}")

        return permissions_mask

    def _serialize_role(self, role) -> RoleResponseDTO:
        """Сериализация роли"""
        return RoleResponseDTO(
            id=str(role.id),
            name=role.name,
            display_name=role.display_name,
            description=role.description,
            permissions=role.permissions,
            permissions_list=[p.name for p in role.permissions_list] if hasattr(
                role.permissions_list, '__iter__') else [],
            is_system=role.is_system,
            is_active=role.is_active,
            created_at=role.created_at.isoformat() if role.created_at else None,
            updated_at=role.updated_at.isoformat() if role.updated_at else None
        )
