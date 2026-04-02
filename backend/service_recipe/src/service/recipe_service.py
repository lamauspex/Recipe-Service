""" Сервис для работы с рецептами """

from uuid import UUID

from backend.service_recipe.src.schemas import RecipeCreate, RecipeResponse
from backend.service_recipe.src.protocols.recipe_repository import (
    RecipeRepositoryProtocol)
from backend.service_recipe.src.service.mappers import RecipeMapper


class RecipeService:
    """Сервис бизнес-логики для рецептов"""

    def __init__(
        self,
        recipe_repo: RecipeRepositoryProtocol
    ):
        self.recipe_repo = recipe_repo

    def create_recipe(
        self,
        recipe_data: RecipeCreate,
        user_id: UUID
    ) -> RecipeResponse:
        """
        Создаёт рецепт

        Args:
            recipe_data: Данные рецепта от клиента
            user_id: ID автора рецепта (из токена)

        Returns:
            Созданный рецепт для клиента
        """
        # Преобразуем ингредиенты в формат для репозитория
        ingredients_data = [
            {
                "ingredient": ing.name,
                "quantity": ing.quantity,
                "unit": ing.unit
            }
            for ing in recipe_data.ingredients
        ]

        # Репозиторий создаёт рецепт в БД и возвращает модель Recipe
        recipe = self.recipe_repo.create(
            user_id=user_id,
            name_recipe=recipe_data.name_recipe,
            description=recipe_data.description,
            ingredients_data=ingredients_data
        )

        # Маппим модель БД в HTTP ответ для клиента
        return RecipeMapper.to_response(recipe)
