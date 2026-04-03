"""
Тесты сервисного слоя RecipeService
"""

from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from backend.service_recipe.src.schemas import RecipeCreate, IngredientSchema
from backend.service_recipe.src.service.recipe_service import RecipeService


class TestRecipeService:
    """Тесты RecipeService"""

    @pytest.fixture
    def mock_recipe_model(self):
        """Создаёт мок модели рецепта из БД"""

        recipe_id = uuid4()
        user_id = uuid4()

        # Мок ингредиента
        ingredient = Mock()
        ingredient.id = uuid4()
        ingredient.ingredient = "Свекла"
        ingredient.quantity = "300"
        ingredient.unit = "г"

        # Мок рецепта
        recipe = Mock()
        recipe.id = recipe_id
        recipe.user_id = user_id
        recipe.name_recipe = "Борщ"
        recipe.description = "Вкусный украинский борщ"
        recipe.ingredients = [ingredient]
        recipe.created_at = datetime.now()
        recipe.updated_at = None

        return recipe

    @pytest.fixture
    def recipe_create_data(self):
        """Данные для создания рецепта"""
        return RecipeCreate(
            name_recipe="Борщ",
            description="Вкусный украинский борщ",
            ingredients=[
                IngredientSchema(
                    ingredient="Свекла",
                    quantity="300",
                    unit="г"
                ),
                IngredientSchema(
                    ingredient="Капуста",
                    quantity="200",
                    unit="г"
                ),
            ]
        )

    def test_create_recipe_returns_response(
            self, mock_recipe_repo,
            mock_recipe_model, recipe_create_data):
        """Создание рецепта должно возвращать RecipeResponse"""
        user_id = uuid4()

        # Настраиваем мок
        mock_recipe_repo.create.return_value = mock_recipe_model

        service = RecipeService(recipe_repo=mock_recipe_repo)
        result = service.create_recipe(
            recipe_data=recipe_create_data,
            user_id=user_id
        )

        # Проверяем результат
        assert result is not None
        assert result.name_recipe == "Борщ"
        assert result.description == "Вкусный украинский борщ"
        assert len(result.ingredients) == 1

    def test_create_recipe_calls_repo_with_correct_data(
            self, mock_recipe_repo, mock_recipe_model,
            recipe_create_data):
        """Сервис должен передавать правильные данные в репозиторий"""
        user_id = uuid4()

        mock_recipe_repo.create.return_value = mock_recipe_model

        service = RecipeService(recipe_repo=mock_recipe_repo)
        service.create_recipe(recipe_data=recipe_create_data, user_id=user_id)

        # Проверяем, что репозиторий был вызван с правильными аргументами
        mock_recipe_repo.create.assert_called_once()

        call_kwargs = mock_recipe_repo.create.call_args.kwargs
        assert call_kwargs['user_id'] == user_id
        assert call_kwargs['name_recipe'] == "Борщ"
        assert call_kwargs['description'] == "Вкусный украинский борщ"

    def test_create_recipe_maps_ingredients_correctly(
            self, mock_recipe_repo, mock_recipe_model,
            recipe_create_data):
        """Ингредиенты должны маппиться правильно в формат для БД"""
        user_id = uuid4()

        mock_recipe_repo.create.return_value = mock_recipe_model

        service = RecipeService(recipe_repo=mock_recipe_repo)
        service.create_recipe(recipe_data=recipe_create_data, user_id=user_id)

        # Проверяем структуру ингредиентов
        call_kwargs = mock_recipe_repo.create.call_args.kwargs
        ingredients_data = call_kwargs['ingredients_data']

        assert len(ingredients_data) == 2
        assert ingredients_data[0] == {
            "ingredient": "Свекла",
            "quantity": "300",
            "unit": "г"
        }
        assert ingredients_data[1] == {
            "ingredient": "Капуста",
            "quantity": "200",
            "unit": "г"
        }

    def test_create_recipe_with_empty_ingredients(self, mock_recipe_repo):
        """Создание рецепта без ингредиентов должно работать"""
        user_id = uuid4()

        # Мок рецепта без ингредиентов
        mock_recipe = Mock()
        mock_recipe.id = uuid4()
        mock_recipe.name_recipe = "Чай"
        mock_recipe.description = "Просто чай"
        mock_recipe.ingredients = []
        mock_recipe.created_at = datetime.now()
        mock_recipe.updated_at = None

        mock_recipe_repo.create.return_value = mock_recipe

        recipe_data = RecipeCreate(
            name_recipe="Чай",
            description="Просто чай",
            ingredients=[]
        )

        service = RecipeService(recipe_repo=mock_recipe_repo)
        result = service.create_recipe(
            recipe_data=recipe_data, user_id=user_id)

        assert result.name_recipe == "Чай"
        assert len(result.ingredients) == 0

    def test_create_recipe_returns_correct_response_fields(
            self, mock_recipe_repo,
            mock_recipe_model, recipe_create_data):
        """Response должен содержать все необходимые поля"""
        user_id = uuid4()

        mock_recipe_repo.create.return_value = mock_recipe_model

        service = RecipeService(recipe_repo=mock_recipe_repo)
        result = service.create_recipe(
            recipe_data=recipe_create_data, user_id=user_id)

        # Проверяем все поля ответа
        assert hasattr(result, 'id')
        assert hasattr(result, 'name_recipe')
        assert hasattr(result, 'description')
        assert hasattr(result, 'ingredients')
        assert hasattr(result, 'created_at')
        assert hasattr(result, 'updated_at')
