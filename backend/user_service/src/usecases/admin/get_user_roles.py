"""
Usecase для получения ролей пользователя
"""

from uuid import UUID

from ...schemas.requests import UserRoleRequestDTO
from ...schemas.responses import UserRoleResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException
from ....models.user_models import User
from ...infrastructure.repositories.user_repository import UserRepository


class GetUserRolesUsecase(BaseUsecase):
    """Usecase для получения ролей пользователя"""

    def __init__(self, user_repository: UserRepository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: UserRoleRequestDTO
    ) -> UserRoleResponseDTO:
        """Выполнение получения ролей пользователя"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException("User not found")

            # Получение ролей
            roles = []
            for role in user.roles:
                roles.append(self._serialize_role(role))

            # Возврат результата
            return UserRoleResponseDTO.create_success(
                user_id=str(request.user_id),
                roles=roles
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to get user roles: {str(e)}")

    def _serialize_role(self, role) -> dict:
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
