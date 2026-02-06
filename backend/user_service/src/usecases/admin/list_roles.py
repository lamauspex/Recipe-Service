"""
Usecase для получения списка ролей
"""

from ...schemas.requests import BaseRequestDTO
from ...schemas.responses import RoleListResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException
from ....models.role_model import RoleModel
from ...infrastructure.repositories.role_repository import RoleRepository


class ListRolesUsecase(BaseUsecase):
    """Usecase для получения списка ролей"""

    def __init__(self, role_repository: RoleRepository, **kwargs):
        self.role_repository = role_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: BaseRequestDTO
    ) -> RoleListResponseDTO:
        """Выполнение получения списка ролей"""
        try:
            # Получение всех активных ролей
            roles = await self.role_repository.get_all_active()

            # Сериализация ролей
            serialized_roles = []
            for role in roles:
                serialized_roles.append(self._serialize_role(role))

            # Возврат результата
            return RoleListResponseDTO.create_success(
                roles=serialized_roles,
                total=len(serialized_roles)
            )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise e
            raise ValidationException(f"Failed to list roles: {str(e)}")

    def _serialize_role(self, role: RoleModel) -> dict:
        """Сериализация роли"""
        return {
            "id": str(role.id),
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "permissions": role.permissions,
            "permissions_list": [p.name for p in role.permissions_list],
            "is_system": role.is_system,
            "is_active": role.is_active,
            "created_at": role.created_at.isoformat() if role.created_at else None,
            "updated_at": role.updated_at.isoformat() if role.updated_at else None
        }
