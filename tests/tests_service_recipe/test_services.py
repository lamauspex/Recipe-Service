from unittest.mock import Mock

from backend.service_recipe.src.service.recipe_service import RecipeService


class TestRecipeService:
    """Тесты RecipeService"""

    def test_create_recipe_returns_response(self, mock_recipe_repo):
        """Создание рецепта должно возвращать Response"""
        # Мокаем репозиторий
        mock_recipe_repo.create.return_value = Mock(
            id="uuid",
            user_id="uuid",
            name_recipe="Борщ",
            description="Вкусный",
            ingredients=[]
        )

        service = RecipeService(recipe_repo=mock_recipe_repo)
        # ... вызов и проверка

    def test_create_recipe_calls_repo_with_correct_data(self, mock_recipe_repo):
        """Сервис должен передавать правильные данные в репозиторий"""
        # Проверяем, что данные передаются корректно

    def test_create_recipe_maps_ingredients_correctly(self, mock_recipe_repo):
        """Ингредиенты должны маппиться правильно"""
