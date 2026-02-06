"""
DTO для запроса списка пользователей
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class SortOrder(str, Enum):
    """Порядок сортировки"""
    ASC = "asc"
    DESC = "desc"


class SortBy(str, Enum):
    """Поля для сортировки"""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    EMAIL = "email"
    USERNAME = "username"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"


class ListUsersRequestDTO(BaseModel):
    """DTO для запроса списка пользователей с пагинацией и фильтрацией"""

    page: int = Field(1, ge=1, description="Номер страницы")
    per_page: int = Field(
        20, ge=1, le=100, description="Количество записей на странице")

    # Фильтры
    search: Optional[str] = Field(
        None, description="Поиск по email, username, имени")
    is_active: Optional[bool] = Field(
        None, description="Фильтр по статусу активности")
    is_verified: Optional[bool] = Field(
        None, description="Фильтр по статусу верификации")
    role: Optional[str] = Field(None, description="Фильтр по роли")

    # Сортировка
    sort_by: SortBy = Field(
        SortBy.CREATED_AT, description="Поле для сортировки")
    sort_order: SortOrder = Field(
        SortOrder.DESC, description="Порядок сортировки")

    class Config:
        schema_extra = {
            "example": {
                "page": 1,
                "per_page": 20,
                "search": "john",
                "is_active": True,
                "is_verified": True,
                "role": "user",
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }
