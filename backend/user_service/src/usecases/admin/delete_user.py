"""
Usecase для удаления пользователя (мягкое удаление)
"""

from uuid import UUID
from datetime import datetime

from ..base import BaseUsecase
from ...schemas.requests import UserDeleteRequestDTO
from ...schemas.responses import UserDeleteResponseDTO
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException
)


class DeleteUserUsecase(BaseUsecase):
    """Usecase для удаления пользователя (мягкое удаление)"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: UserDeleteRequestDTO
    ) -> UserDeleteResponseDTO:
        """Выполнение удаления пользователя"""
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

            # Мягкое удаление - деактивация и установка специального флага
            update_data = {
                'is_active': False,
                'is_deleted': True,
                'deleted_at': datetime.utcnow(),
                # Модификация email для избежания конфликтов
                'email': f"deleted_{user.email}",
                'lock_reason': 'Deleted by admin'
            }

            # Обновление пользователя
            updated_user = await self.user_repository.update(
                request.user_id,
                update_data
            )

            if not updated_user:
                raise ValidationException("Failed to delete user")

            # Возврат результата
            return UserDeleteResponseDTO.create_success(
                user_id=int(request.user_id)
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to delete user: {str(e)}")
