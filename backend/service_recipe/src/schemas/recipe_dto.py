"""
DTO для общения между сервисами
"""


from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecipeDTO(BaseModel):
    """
    Data Transfer Object для передачи данных рецепта между сервисами.

    Используется при:
        - Вызове методов других сервисов
        - Внутреннем преобразовании данных
        - Кешировании данных рецепта

    Attributes:
        id: Уникальный идентификатор рецепта
        user_id: ID создателя рецепта (может быть None для демо-режима)
        name_recipe: Название рецепта
        description: Описание рецепта
        created_at: Время создания записи
        updated_at: Время последнего обновления (None если не обновлялся)
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "name_recipe": "Борщ",
                "description": "Традиционный украинский борщ",
                "created_at": "2026-03-15T10:00:00Z",
                "updated_at": None
            }
        }
    )

    id: UUID = Field(
        ...,
        description="Уникальный идентификатор"
    )
    user_id: UUID | None = Field(
        description="ID создателя рецепта"
    )
    name_recipe: str = Field(
        ...,
        description="Название рецепта"
    )
    description: str = Field(
        ...,
        description="Описание рецепта"
    )
    created_at: datetime = Field(
        ...,
        description="Время создания"
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Время последнего обновления"
    )
