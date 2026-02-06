"""
Usecase для получения пользователя по ID
"""

from typing import Dict, Any
from uuid import UUID

from ...schemas.requests import BaseRequestDTO
from ...schemas.responses import UserDetailResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException


class GetUserByIdUsecase(BaseUsecase):
    """Usecase для получения пользователя по ID"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: BaseRequestDTO) -> UserDetailResponseDTO:
        """Выполнение получения пользователя по ID"""
        try:
            # Валидация UUID
            if not hasattr(request, 'user_id'):
                raise ValidationException("user_id is required")

            try:
                UUID(request.user_id)
            except ValueError:
                raise ValidationException("Invalid user ID format")

            # Получение пользователя из репозитория
            user = await self.user_repository.get_by_id(request.user_id)

            if not user:
                raise NotFoundException("User not found")

            # Преобразование данных
            user_detail_data = {
                "id": str(user.id),
                "user_name": getattr(user, 'user_name', None),
                "email": user.email,
                "full_name": getattr(user, 'full_name', f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}"),
                "first_name": getattr(user, 'first_name', None),
                "last_name": getattr(user, 'last_name', None),
                "phone": getattr(user, 'phone', None),
                "is_active": user.is_active,
                "email_verified": getattr(user, 'email_verified', False),
                "is_locked": getattr(user, 'is_locked', False),
                "locked_until": user.locked_until.isoformat() if getattr(user, 'locked_until', None) else None,
                "lock_reason": getattr(user, 'lock_reason', None),
                "last_login": user.last_login.isoformat() if getattr(user, 'last_login', None) else None,
                "login_count": getattr(user, 'login_count', 0),
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "roles": [self._serialize_role(role) for role in getattr(user, 'roles', [])]
            }

            # Возврат результата
            return UserDetailResponseDTO.create_success(user_detail_data)

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to get user: {str(e)}")

    def _serialize_role(self, role) -> dict:
        """Сериализация роли"""
        return {
            "id": str(role.id),
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "permissions": getattr(role, 'permissions', 0),
            "is_system": getattr(role, 'is_system', False),
            "is_active": getattr(role, 'is_active', True),
            "created_at": role.created_at.isoformat() if getattr(role, 'created_at', None) else None
        }
