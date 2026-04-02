"""
Схемы для сервиса рецептов.

Содержит:
    - ingredient_schema: Схемы ингредиентов
    - recipe_request: Схемы входящих запросов
    - recipe_response: Схемы ответов API
    - recipe_dto: DTO для межсервисного общения
    - base: Базовые схемы с валидаторами
"""

from .ingredient_schema import IngredientSchema, IngredientResponse
from .recipe_request import RecipeCreate
from .recipe_response import RecipeResponse
from .base import TitleValidatedModel, DescriptionValidatedModel
from .recipe_dto import RecipeDTO


__all__ = [
    "IngredientSchema",
    "IngredientResponse",
    "RecipeCreate",
    "RecipeResponse",
    "TitleValidatedModel",
    "DescriptionValidatedModel",
    "RecipeDTO"
]
