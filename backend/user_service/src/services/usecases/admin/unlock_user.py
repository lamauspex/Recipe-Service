"""
Usecase для разблокировки пользователя
"""

from uuid import UUID

from ...dto.requests import UserUnlockRequestDTO
from ...dto.responses import UserUnlockResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException
from ....models.user_models import User


class UnlockUserUsecase(BaseUsecase):
    """Usecase для разблокировки пользователя"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: UserUnlockRequestDTO
    ) -> UserUnlockResponseDTO:
        """Выполнение разблокировки пользователя"""
        try:
            # Валидация UUID
            try:
                user_id = UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Получение пользователя
            user = await self.user_repository.get_by_id(str(user_id))
            if not user:
                raise NotFoundException("User not found")

            # Проверка, что пользователь заблокирован
            if not user.is_locked:
                raise ValidationException("User is not locked")

            # Разблокировка пользователя
            unlock_data = {
                "is_locked": False,
                "locked_until": None,
                "lock_reason": None
            }

            updated_user = await self.user_repository.update(str(user_id), unlock_data)
            if not updated_user:
                raise ValidationException("Failed to unlock user")

            # Возврат результата
            return UserUnlockResponseDTO.create_success(
                user_id=str(user_id)
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to unlock user: {str(e)}")
