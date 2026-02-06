"""
Usecase для получения роли по ID
"""

from uuid import UUID

from ...dto.requests import BaseRequestDTO
from ...dto.responses import BaseResponseDTO, RoleResponseDTO
from ..base import BaseUsecase, ResponseBuilder
from ...infrastructure.common.exceptions import NotFoundException, ValidationException
from ....models.role_model import RoleModel
from ...infrastructure.repositories.role_repository import RoleRepository


class GetRoleUsecase(BaseUsecase):
    """Usecase для получения роли по ID"""

    def __init__(self, role_repository: RoleRepository, **kwargs):
        self.role_repository = role_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: BaseRequestDTO
    ) -> BaseResponseDTO:
        """Выполнение получения роли"""
        try:
            # Валидация UUID роли
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

            # Возврат результата
            return BaseResponseDTO(
                success=True,
                data={
                    "role": self._serialize_role(role)
                },
                message="Role retrieved successfully"
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to get role: {str(e)}")

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
