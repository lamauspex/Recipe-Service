""" Схема ответа для HTTP (клиенту) """


from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.service_recipe.src.schemas import IngredientResponse


class RecipeResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,  # Позволяет создавать из ORM объектов
        json_schema_extra={    # Пример для документации
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

    id: UUID
    name_recipe: str
    description: str
    ingredients: list[IngredientResponse]

    created_at: datetime
    updated_at: datetime | None
