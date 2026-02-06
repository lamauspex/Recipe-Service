"""
Usecase для обновления данных пользователя
"""

from uuid import UUID

from ...schemas.requests import UserUpdateRequestDTO
from ...schemas.responses import UserUpdateResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException
from ....models.user_models import User


class UpdateUserUsecase(BaseUsecase):
    """Usecase для обновления данных пользователя"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: UserUpdateRequestDTO
    ) -> UserUpdateResponseDTO:
        """Выполнение обновления данных пользователя"""
        try:
            # Валидация UUID
            if not hasattr(request, 'user_id'):
                raise ValidationException("user_id is required")

            try:
                user_id = UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Получение пользователя
            user = await self.user_repository.get_by_id(str(user_id))
            if not user:
                raise NotFoundException("User not found")

            # Подготовка данных для обновления
            update_data = {}

            if request.first_name is not None:
                update_data["first_name"] = request.first_name

            if request.last_name is not None:
                update_data["last_name"] = request.last_name

            if request.phone is not None:
                update_data["phone"] = request.phone

            if request.is_active is not None:
                update_data["is_active"] = request.is_active

            # Проверка, что есть данные для обновления
            if not update_data:
                raise ValidationException("No data provided for update")

            # Обновление пользователя
            updated_user = await self.user_repository.update(str(user_id), update_data)
            if not updated_user:
                raise ValidationException("Failed to update user")

            # Возврат результата
            return UserUpdateResponseDTO.create_success(
                user=self._serialize_user(updated_user)
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to update user: {str(e)}")

    def _serialize_user(self, user: User) -> dict:
        """Сериализация пользователя"""
        return {
            "id": str(user.id),
            "user_name": user.user_name,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
