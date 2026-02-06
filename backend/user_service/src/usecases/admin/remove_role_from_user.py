"""
Usecase для удаления роли у пользователя
"""

from uuid import UUID

from ...schemas.requests import RoleRemoveRequestDTO
from ...schemas.responses import BaseResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException
from ....models.user_models import User
from ....models.role_model import RoleModel


class RemoveRoleFromUserUsecase(BaseUsecase):
    """Usecase для удаления роли у пользователя"""

    def __init__(self, user_repository, role_repository, **kwargs):
        self.user_repository = user_repository
        self.role_repository = role_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: RoleRemoveRequestDTO
    ) -> BaseResponseDTO:
        """Выполнение удаления роли у пользователя"""
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

            # Проверка наличия роли у пользователя
            if role not in user.roles:
                raise ValidationException("User does not have this role")

            # Проверка системной роли (системные роли нельзя удалять)
            if role.is_system:
                raise ValidationException("Cannot remove system role")

            # Удаление роли у пользователя
            user.remove_role(role)
            await self.user_repository.update(user.id, {"roles": user.roles})

            # Возврат результата
            return BaseResponseDTO(
                success=True,
                message="Role removed from user successfully",
                data={
                    "user_id": str(user_id),
                    "role_id": str(role_id)
                }
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(
                f"Failed to remove role from user: {str(e)}")
