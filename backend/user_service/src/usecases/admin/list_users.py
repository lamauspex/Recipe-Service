"""
Usecase для получения списка пользователей с пагинацией и фильтрацией
Мигрирован из старой архитектуры
"""

from typing import Dict, Any, List, Tuple
from math import ceil

from ...schemas.requests import ListUsersRequestDTO
from ...schemas.responses import UsersListResponseDTO, UserListItem, PaginationInfo
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException


class ListUsersUsecase(BaseUsecase):
    """Usecase для получения списка пользователей с пагинацией и фильтрацией"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: ListUsersRequestDTO) -> UsersListResponseDTO:
        """Выполнение получения списка пользователей"""
        try:
            # Подготовка параметров запроса
            query_params = self._prepare_query_params(request)

            # Получение пользователей из репозитория
            users_data = await self.user_repository.list_users_with_pagination(
                page=request.page,
                per_page=request.per_page,
                search=request.search,
                is_active=request.is_active,
                is_verified=request.is_verified,
                role=request.role,
                sort_by=request.sort_by,
                sort_order=request.sort_order
            )

            # Формирование ответа
            users_list = []
            for user_data in users_data.get("users", []):
                user_item = UserListItem(
                    id=user_data["id"],
                    email=user_data["email"],
                    username=user_data["username"],
                    first_name=user_data.get("first_name"),
                    last_name=user_data.get("last_name"),
                    role=user_data["role"],
                    is_active=user_data["is_active"],
                    is_verified=user_data.get("is_verified", False),
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"]
                )
                users_list.append(user_item)

            # Создание информации о пагинации
            total = users_data.get("total", 0)
            total_pages = ceil(total / request.per_page) if total > 0 else 0

            pagination = PaginationInfo(
                page=request.page,
                per_page=request.per_page,
                total=total,
                total_pages=total_pages,
                has_next=request.page < total_pages,
                has_prev=request.page > 1
            )

            # Примененные фильтры
            filters_applied = self._get_applied_filters(request)

            return UsersListResponseDTO.create_success(
                users=users_list,
                pagination=pagination,
                filters_applied=filters_applied
            )

        except Exception as e:
            return UsersListResponseDTO.create_error(str(e), "LIST_USERS_ERROR")

    def _prepare_query_params(self, request: ListUsersRequestDTO) -> Dict[str, Any]:
        """Подготовка параметров запроса"""
        params = {
            "page": request.page,
            "per_page": request.per_page
        }

        # Добавляем фильтры, если они указаны
        if request.search:
            params["search"] = request.search.strip()
        if request.is_active is not None:
            params["is_active"] = request.is_active
        if request.is_verified is not None:
            params["is_verified"] = request.is_verified
        if request.role:
            params["role"] = request.role.strip()

        # Сортировка
        params["sort_by"] = request.sort_by
        params["sort_order"] = request.sort_order

        return params

    def _get_applied_filters(self, request: ListUsersRequestDTO) -> Dict[str, Any]:
        """Получение примененных фильтров"""
        filters = {}

        if request.search:
            filters["search"] = request.search
        if request.is_active is not None:
            filters["is_active"] = request.is_active
        if request.is_verified is not None:
            filters["is_verified"] = request.is_verified
        if request.role:
            filters["role"] = request.role

        # Добавляем информацию о сортировке
        filters["sort_by"] = request.sort_by
        filters["sort_order"] = request.sort_order

        return filters
