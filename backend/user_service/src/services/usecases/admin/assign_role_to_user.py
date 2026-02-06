"""Usecase для назначения роли пользователю"""
"""

from uuid import UUID

from ...dto.requests import RoleAssignRequestDTO
from ...dto.responses import RoleAssignResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException, ConflictException
from ....models.user_models import User
from ....models.role_model import RoleModel
from ...infrastructure.repositories.user_repository import UserRepository
from ...infrastructure.repositories.role_repository import RoleRepository


class AssignRoleToUserUsecase(BaseUsecase):
    """Usecase для назначения роли пользователю"""

    def __init__(self, user_repository: UserRepository, role_repository: RoleRepository, **kwargs):
        self.user_repository = user_repository
        self.role_repository = role_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: RoleAssignRequestDTO
    ) -> RoleAssignResponseDTO:
        """Выполнение назначения роли пользователю"""
        try:
            # Валидация UUID
            try:
                user_id = UUID(request.user_id)
                role_id = UUID(request.role_id)
            except ValueError:
                raise ValidationException("Invalid user ID or role ID format")

            # Получение пользователя
            user = await self.user_repository.get_by_id(str(user_id))
            if not user:
                raise NotFoundException("User not found")

            # Получение роли
            role = await self.role_repository.get_by_id(str(role_id))
            if not role:
                raise NotFoundException("Role not found")

            # Проверка, что роль активна
            if not role.is_active:
                raise ValidationException("Cannot assign inactive role")

            # Проверка, есть ли уже эта роль у пользователя
            user_roles = await self.user_repository.get_user_roles(str(user_id))
            if any(str(r.id) == str(role_id) for r in user_roles):
                raise ConflictException("User already has this role")

            # Назначение роли пользователю
            success = await self.user_repository.add_role_to_user(str(user_id), role)
            if not success:
                raise ValidationException("Failed to assign role to user")

            # Возврат результата
            return RoleAssignResponseDTO.create_success(
                user_id=str(user_id),
                role_id=str(role_id)
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException, ConflictException)):
                raise e
            raise ValidationException(
                f"Failed to assign role to user: {str(e)}")
