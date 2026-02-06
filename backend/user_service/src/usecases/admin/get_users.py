"""
Usecase для получения списка пользователей
"""

from typing import Dict, Any
from uuid import UUID

from ...schemas.requests import UserListRequestDTO
from ...schemas.responses import UserListResponseDTO, UserResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException


class GetUsersUsecase(BaseUsecase):
    """Usecase для получения списка пользователей с фильтрацией"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: UserListRequestDTO) -> UserListResponseDTO:
        """Выполнение получения списка пользователей"""
        try:
            # Валидация параметров
            if request.page < 1:
                raise ValidationException("Page must be greater than 0")

            if request.per_page < 1 or request.per_page > 100:
                raise ValidationException("Per page must be between 1 and 100")

            # Получение данных из репозитория
            users_data, total = await self.user_repository.get_list(request)

            # Преобразование в DTO
            users = []
            for user in users_data:
                user_dto = UserResponseDTO(
                    id=int(user.id),
                    email=user.email,
                    first_name=getattr(user, 'first_name', ''),
                    last_name=getattr(user, 'last_name', ''),
                    phone=getattr(user, 'phone', None),
                    role=getattr(user, 'role', 'user'),
                    is_active=user.is_active,
                    is_verified=getattr(user, 'email_verified', False),
                    created_at=user.created_at,
                    updated_at=user.updated_at
                )
                users.append(user_dto)

            # Возврат результата
            return UserListResponseDTO.create_success(
                users=users,
                total=total,
                page=request.page,
                per_page=request.per_page
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to get users list: {str(e)}")
