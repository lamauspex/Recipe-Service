"""
Схема ответа для HTTP (клиенту)
"""


from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.service_recipe.src.schemas import IngredientResponse


class RecipeResponse(BaseModel):
    """
    Схема ответа с данными рецепта.

    Используется для возврата рецепта в HTTP ответах.
    Содержит полную информацию о рецепте включая ингредиенты.

    Attributes:
        id: Уникальный идентификатор рецепта
        name_recipe: Название рецепта
        description: Описание рецепта
        ingredients: Список ингредиентов
        created_at: Время создания
        updated_at: Время последнего обновления
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name_recipe": "Борщ",
                "description": "Традиционный украинский борщ",
                "ingredients": [
                    {"id": "...",
                     "name": "Свекла",
                     "quantity": "300",
                     "unit": "г"}
                ],
                "created_at": "2026-03-15T10:00:00Z"
            }
        }
    )

    id: UUID = Field(
        ...,
        description="Уникальный идентификатор"
    )
    user_id: UUID = Field(
        ...,
        description="ID создателя"
    )

    name_recipe: str = Field(
        ...,
        description="Название рецепта"
    )
    description: str = Field(
        ...,
        description="Описание рецепта"
    )
    ingredients: list[IngredientResponse] = Field(
        ...,
        description="Список ингредиентов"
    )
    created_at: datetime = Field(
        ...,
        description="Время создания"
    )
    updated_at: datetime | None = Field(
        default=None,
        description="Время последнего обновления"
    )
