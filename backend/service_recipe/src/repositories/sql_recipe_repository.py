"""Репозиторий для работы с рецептами в БД"""

from uuid import UUID
from sqlalchemy.orm import Session

from backend.service_recipe.src.models import Recipe, Ingredient


class SQLRecipeRepository:
    """Репозиторий для операций с рецептами"""

    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        user_id: UUID,
        name_recipe: str,
        description: str,
        ingredients_data: list[dict]
    ) -> Recipe:
        """
        Создаёт рецепт в БД

        Args:
            user_id: ID пользователя-автора
            name_recipe: Название рецепта
            description: Описание
            ingredients_data: Список ингредиентов [{
                "ingredient": "...",
                "quantity": "...",
                "unit": "..."
                }]

        Returns:
            Созданный объект Recipe
        """
        # Создаём рецепт
        recipe = Recipe(
            user_id=user_id,
            name_recipe=name_recipe,
            description=description
        )
        # Добавляем в сессию
        self._session.add(recipe)
        self._session.flush()  # Получаем ID рецепта до коммита

        for ing_data in ingredients_data:
            ingredient = Ingredient(
                recipe_id=recipe.id,
                ingredient=ing_data["ingredient"],
                quantity=ing_data["quantity"],
                unit=ing_data["unit"]
            )
            self._session.add(ingredient)

        # Коммитим всё
        self._session.commit()
        self._session.refresh(recipe)  # Обновляем объект с данными из БД

        return recipe

    def get_by_id(self, recipe_id: UUID) -> Recipe | None:
        """ Получает рецепт по ID """
        return self._session.query(Recipe).filter(
            Recipe.id == recipe_id).first()
