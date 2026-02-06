"""
Usecase для получения пользователя по ID
"""

from typing import Dict, Any
from uuid import UUID

from ...dto.responses import UserDetailResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException


class GetUserByIdUsecase(BaseUsecase):
    """Usecase для получения пользователя по ID"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, user_id: str) -> UserDetailResponseDTO:
        """Выполнение получения пользователя по ID"""
        try:
            # Валидация UUID
            try:
                UUID(user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Получение пользователя из репозитория
            user_data = await self.user_repository.get_by_id(user_id)

            if not user_data:
                raise NotFoundException("User not found")

            # Преобразование данных
            user_detail_data = {
                "id": str(user_data['id']),
                "user_name": user_data.get('user_name'),
                "email": user_data['email'],
                "full_name": user_data.get('full_name'),
                "first_name": user_data.get('first_name'),
                "last_name": user_data.get('last_name'),
                "phone": user_data.get('phone'),
                "is_active": user_data['is_active'],
                "email_verified": user_data.get('email_verified', False),
                "is_locked": user_data.get('is_locked', False),
                "locked_until": user_data['locked_until'].isoformat() if user_data.get('locked_until') else None,
                "lock_reason": user_data.get('lock_reason'),
                "last_login_at": user_data['last_login_at'].isoformat() if user_data.get('last_login_at') else None,
                "last_login_ip": user_data.get('last_login_ip'),
                "created_at": user_data['created_at'].isoformat(),
                "updated_at": user_data['updated_at'].isoformat(),
                "roles": user_data.get('roles', [])
            }

            # Возврат результата
            return UserDetailResponseDTO.create_success(user_detail_data)

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to get user: {str(e)}")
