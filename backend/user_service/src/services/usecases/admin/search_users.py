"""
Usecase для поиска пользователей
"""

from typing import Dict, Any, List
from uuid import UUID

from ...dto.requests import UserSearchRequestDTO
from ...dto.responses import UserSearchResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException


class SearchUsersUsecase(BaseUsecase):
    """Usecase для поиска пользователей"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: UserSearchRequestDTO) -> UserSearchResponseDTO:
        """Выполнение поиска пользователей"""
        try:
            # Валидация поискового запроса
            if not request.search_term or len(request.search_term.strip()) < 2:
                raise ValidationException("Search term must be at least 2 characters long")

            if request.limit < 1 or request.limit > 100:
                raise ValidationException("Limit must be between 1 and 100")

            search_term = request.search_term.strip()

            # Поиск пользователей
            users_data = await self.user_repository.search_users(
                search_term=search_term,
                limit=request.limit
            )

            # Форматирование результатов
            results = []
            for user_data in users_data:
                result = {
                    "id": str(user_data['id']),
                    "email": user_data['email'],
                    "full_name": user_data.get('full_name') or f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}",
                    "phone": user_data.get('phone'),
                    "is_active": user_data['is_active'],
                    "is_verified": user_data.get('is_verified', False),
                    "last_login_at": user_data['last_login_at'].isoformat() if user_data.get('last_login_at') else None,
                    "created_at": user_data['created_at'].isoformat()
                }
                results.append(result)

            # Возврат результата
            return UserSearchResponseDTO.create_success(
                search_term=search_term,
                results=results,
                total_found=len(results)
            )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise e
            raise ValidationException(f"Failed to search users: {str(e)}")
