
from typing import Protocol, Optional

from uuid import UUID

from backend.service_recipe.src.models import Recipe


class RecipeRepositoryProtocol(Protocol):
    """
    Интерфейс репозитория для работы с рецептами

    Любой класс, реализующий эти методы, может быть использован
    как RecipeRepositoryProtocol. Не нужно наследоваться!

    """

    def create(
        self,
        user_id: UUID,
        name_recipe: str,
        description: str,
        ingredients_data: list[dict]
    ) -> Recipe:
        """
        Создание рецепта в БД

        Args:
            user_id: ID пользователя-автора
            name_recipe: Название рецепта
            description: Описание
            ingredients_data: Список ингредиентов

        Returns:
            Созданный объект Recipe
        """
        ...

    def get_by_id(self, recipe_id: UUID) -> Optional[Recipe]:
        """
        Получение рецепта по id

        :param recipe_id: ID рецепта
        :return: Рецепт или None
        """
        ...
