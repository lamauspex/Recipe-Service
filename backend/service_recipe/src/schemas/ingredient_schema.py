"""
Схемы для Ingredient
"""

from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MeasurementUnit(str, Enum):
    """Единицы измерения ингредиентов"""

    GRAM = "г"
    KILOGRAM = "кг"
    MILLILITER = "мл"
    LITER = "л"
    TEASPOON = "ч.л."
    TABLESPOON = "ст.л."
    PIECE = "шт"


class IngredientSchema(BaseModel):
    """
        Схема ингредиента для входящих запросов

    Используется при создании/обновлении рецепта

    Attributes:
        name: Название ингредиента (обязательно)
        quantity: Количество с единицей измерения (обязательно)
        unit: Единица измерения (опционально)

    Example:
        >>> ingredient = IngredientSchema(
        ...     name="Свекла",
        ...     quantity="300",
        ...     unit="г"
        ... )
    """

    name: str
    quantity: str
    unit: Annotated[MeasurementUnit | None, Field(default=None)]


class IngredientResponse(BaseModel):
    """
    Схема ингредиента для исходящих ответов API

    Используется в RecipeResponse для отображения
    списка ингредиентов готового рецепта.

    Attributes:
        id: Уникальный идентификатор ингредиента
        name: Название ингредиента
        quantity: Количество с единицей измерения
        unit: Единица измерения
    """

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Свекла",
                "quantity": "300",
                "unit": "г"
            }
        }
    )

    id: UUID
    name: str
    quantity: str
    unit: str
