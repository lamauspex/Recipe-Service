"""
Usecase для получения списка пользователей
"""

from typing import Dict, Any
from uuid import UUID

from ...dto.requests import UserListRequestDTO
from ...dto.responses import UserListResponseDTO, UserResponseDTO
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

            # Построение фильтров
            filters = {}

            if request.search:
                filters['search'] = request.search

            if request.is_active is not None:
                filters['is_active'] = request.is_active

            if request.is_locked is not None:
                filters['is_locked'] = request.is_locked

            # Получение данных из репозитория
            users_data = await self.user_repository.get_users_with_pagination(
                page=request.page,
                per_page=request.per_page,
                **filters
            )

            # Преобразование в DTO
            users = []
            for user_data in users_data.get('users', []):
                user_dto = UserResponseDTO(
                    id=user_data['id'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone=user_data.get('phone'),
                    role=user_data['role'],
                    is_active=user_data['is_active'],
                    is_verified=user_data.get('is_verified', False),
                    created_at=user_data['created_at'],
                    updated_at=user_data['updated_at']
                )
                users.append(user_dto)

            # Возврат результата
            return UserListResponseDTO.create_success(
                users=users,
                total=users_data.get('total', 0),
                page=request.page,
                per_page=request.per_page
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to get users list: {str(e)}")
