"""
DTO для ответа со списком пользователей
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class UserListItem(BaseModel):
    """Элемент списка пользователей"""
    
    id: UUID
    email: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PaginationInfo(BaseModel):
    """Информация о пагинации"""
    
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class UsersListResponseDTO(BaseModel):
    """DTO для ответа со списком пользователей"""
    
    success: bool
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None
    error_code: Optional[str] = None

    # Данные ответа
    users: List[UserListItem] = Field(default_factory=list)
    pagination: Optional[PaginationInfo] = None
    filters_applied: dict = Field(default_factory=dict)

    @classmethod
    def create_success(
        cls, 
        users: List[UserListItem], 
        pagination: PaginationInfo,
        filters_applied: dict,
        message: str = "Список пользователей получен"
    ) -> 'UsersListResponseDTO':
        """Создание успешного ответа"""
        return cls(
            success=True,
            message=message,
            users=users,
            pagination=pagination,
            filters_applied=filters_applied
        )

    @classmethod
    def create_error(cls, error: str, error_code: str = None) -> 'UsersListResponseDTO':
        """Создание ответа с ошибкой"""
        return cls(
            success=False,
            message="Ошибка при получении списка пользователей",
            error=error,
            error_code=error_code
        )

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Список пользователей получен",
                "users": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "username": "user123",
                        "first_name": "John",
                        "last_name": "Doe",
                        "role": "user",
                        "is_active": True,
                        "is_verified": True,
                        "created_at": "2023-01-01T00:00:00Z",
                        "updated_at": "2023-01-01T00:00:00Z"
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 150,
                    "total_pages": 8,
                    "has_next": True,
                    "has_prev": False
                },
                "filters_applied": {
                    "search": "john",
                    "is_active": True,
                    "role": "user"
                }
            }
        }
