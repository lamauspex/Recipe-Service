"""
Usecase для удаления роли
"""

from uuid import UUID

from ...dto.requests import RoleDeleteRequestDTO
from ...dto.responses import RoleDeleteResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException, ConflictException
from ...infrastructure.repositories.role_repository import RoleRepository


class DeleteRoleUsecase(BaseUsecase):
    """Usecase для удаления роли"""

    def __init__(self, role_repository: RoleRepository, **kwargs):
        self.role_repository = role_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: RoleDeleteRequestDTO
    ) -> RoleDeleteResponseDTO:
        """Выполнение удаления роли"""
        try:
            # Валидация UUID
            try:
                role_id = UUID(request.role_id)
            except ValueError:
                raise ValidationException("Invalid role ID format")

            # Получение роли
            role = await self.role_repository.get_by_id(str(role_id))
            if not role:
                raise NotFoundException(
                    f"Role with ID {request.role_id} not found")

            # Проверка системной роли (системные роли нельзя удалять)
            if role.is_system:
                raise ValidationException("Cannot delete system role")

            # Проверка количества пользователей с этой ролью
            user_count = await self.role_repository.get_user_count_for_role(str(role_id))
            if user_count > 0:
                raise ConflictException(
                    f"Cannot delete role that is assigned to {user_count} users"
                )

            # Удаление роли
            success = await self.role_repository.delete(str(role_id))
            if not success:
                raise ValidationException("Failed to delete role")

            # Возврат результата
            return RoleDeleteResponseDTO.create_success(
                role_id=str(role_id)
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException, ConflictException)):
                raise e
            raise ValidationException(f"Failed to delete role: {str(e)}")
