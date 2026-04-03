""" Маппер для конвертации схем """

from backend.service_recipe.src.models import Recipe
from backend.service_recipe.src.schemas import (
    RecipeResponse,
    RecipeDTO
)


class RecipeMapper:
    """Маппер для преобразования рецептов"""

    @staticmethod
    def to_response(recipe: Recipe) -> RecipeResponse:
        """
        Модель БД → HTTP ответ

        Преобразует SQLAlchemy модель в Pydantic схему для клиента.
        """
        return RecipeResponse(
            id=recipe.id,
            name_recipe=recipe.name_recipe,
            description=recipe.description,
            ingredients=[
                {
                    "id": ingredient.id,
                    "ingredient": ingredient.ingredient,
                    "quantity": ingredient.quantity,
                    "unit": ingredient.unit
                }
                for ingredient in recipe.ingredients
            ],
            created_at=recipe.created_at,
            updated_at=recipe.updated_at
        )

    @staticmethod
    def to_dto(recipe: Recipe) -> RecipeDTO:
        """
        Модель БД → DTO

        Для межсервисного общения (RabbitMQ, gRPC).
        """
        return RecipeDTO(
            id=recipe.id,
            user_id=recipe.user_id,
            name_recipe=recipe.name_recipe,
            description=recipe.description,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at
        )
