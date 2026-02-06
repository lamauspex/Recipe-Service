"""Usecase для поиска пользователей"""

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
                raise ValidationException(
                    "Search term must be at least 2 characters long")

            if request.limit < 1 or request.limit > 100:
                raise ValidationException("Limit must be between 1 and 100")

            search_term = request.search_term.strip()

            # Поиск пользователей
            users = await self.user_repository.search_users(search_term, request.limit)

            # Форматирование результатов
            results = []
            for user in users:
                result = {
                    "id": str(user.id),
                    "email": user.email,
                    "first_name": getattr(user, 'first_name', ''),
                    "last_name": getattr(user, 'last_name', ''),
                    "full_name": getattr(user, 'full_name', f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}"),
                    "phone": getattr(user, 'phone', None),
                    "is_active": user.is_active,
                    "is_verified": getattr(user, 'is_verified', False),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "created_at": user.created_at.isoformat() if user.created_at else None
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
