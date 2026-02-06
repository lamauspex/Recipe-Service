"""
Usecase для проверки разрешений пользователя
"""

from uuid import UUID

from ...dto.requests import PermissionCheckRequestDTO
from ...dto.responses import PermissionCheckResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException
from ....models.role_model import Permission


class CheckUserPermissionUsecase(BaseUsecase):
    """Usecase для проверки разрешений пользователя"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: PermissionCheckRequestDTO
    ) -> PermissionCheckResponseDTO:
        """Выполнение проверки разрешений пользователя"""
        try:
            # Валидация UUID
            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Валидация разрешения
            if not hasattr(Permission, request.permission.upper()):
                raise ValidationException(
                    f"Invalid permission: {request.permission}. "
                    f"Available permissions: {[p.name for p in Permission if p != Permission.NONE]}"
                )

            # Получение пользователя
            user = await self.user_repository.get_by_id(request.user_id)
            if not user:
                raise NotFoundException("User not found")

            # Проверка разрешения
            permission_enum = getattr(Permission, request.permission.upper())
            has_permission = user.has_permission(permission_enum)

            # Возврат результата
            return PermissionCheckResponseDTO.create_success(
                user_id=str(request.user_id),
                permission=request.permission,
                has_permission=has_permission
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(
                f"Failed to check user permission: {str(e)}")
