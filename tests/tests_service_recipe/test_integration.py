from unittest.mock import Mock

import pytest

from backend.service_recipe.src.infrastructure.dependencies import get_recipe_service
from backend.service_recipe.src.schemas.recipe_response import RecipeResponse
from backend.service_user.src.app_users import create_app


class TestCreateRecipeEndpoint:
    """Тесты эндпоинта создания рецепта"""

    @pytest.fixture
    def mock_recipe_service(self):
        """Мок RecipeService"""
        mock = Mock()
        mock.create_recipe.return_value = RecipeResponse(...)
        return mock

    @pytest.fixture
    def app(self, mock_recipe_service):
        app = create_app()
        app.dependency_overrides[get_recipe_service] = lambda: mock_recipe_service
        return app

    @pytest.mark.asyncio
    async def test_create_recipe_without_auth_returns_401(self, app):
        """Создание без токена должно возвращать 401"""

    @pytest.mark.asyncio
    async def test_create_recipe_with_valid_data_returns_201(self, app):
        """Создание с валидными данными должно возвращать 201"""

    @pytest.mark.asyncio
    async def test_create_recipe_with_short_title_returns_422(self, app):
        """Слишком короткое название — 422"""

    @pytest.mark.asyncio
    async def test_create_recipe_with_invalid_token_returns_401(self, app):
        """Невалидный токен — 401"""
