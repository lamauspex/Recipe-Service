"""
Интеграционные тесты API эндпоинтов Recipe Service
"""

from datetime import datetime
from unittest.mock import AsyncMock, AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.service_recipe.src.application import create_app


class TestCreateRecipeEndpoint:
    """Тесты эндпоинта создания рецепта"""

    @pytest.fixture
    def mock_user_service_client(self):
        """Мок gRPC клиента для валидации токена"""
        mock = AsyncMock()
        mock.validate_token.return_value = {
            "valid": True,
            "user_id": str(uuid4()),
            "email": "test@example.com"
        }
        return mock

    @pytest.fixture
    def mock_recipe_service(self):
        """Мок RecipeService"""
        recipe_id = uuid4()

        # Мок ингредиента
        ingredient = Mock()
        ingredient.id = uuid4()
        ingredient.ingredient = "Свекла"
        ingredient.quantity = "300"
        ingredient.unit = "г"

        # Мок рецепта
        mock_recipe = Mock()
        mock_recipe.id = recipe_id
        mock_recipe.name_recipe = "Борщ"
        mock_recipe.description = "Вкусный украинский борщ"
        mock_recipe.ingredients = [ingredient]
        mock_recipe.created_at = datetime.now()
        mock_recipe.updated_at = None

        mock = Mock()
        mock.create_recipe.return_value = mock_recipe
        return mock

    @pytest.fixture
    def app(self, mock_user_service_client, mock_recipe_service):
        app = create_app()

        # Переопределяем зависимости правильно
        from backend.service_recipe.src.infrastructure.dependencies import (
            get_user_service_client,
            get_recipe_service,
            get_message_publisher
        )

        app.dependency_overrides[get_user_service_client] = lambda: mock_user_service_client
        app.dependency_overrides[get_recipe_service] = lambda: mock_recipe_service
        mock_publisher = AsyncMock()
        app.dependency_overrides[get_message_publisher] = lambda: mock_publisher

        yield app

    @pytest.fixture
    def client(self, app):
        """TestClient для синхронных тестов"""
        return TestClient(app)

    def test_create_recipe_without_auth_returns_401(self, client):
        """Создание без токена должно возвращать 401"""
        response = client.post(
            "/api/v1/recipe/recipes/",
            json={
                "name_recipe": "Борщ",
                "description": "Вкусный украинский борщ",
                "ingredients": [
                    {"ingredient": "Свекла", "quantity": "300", "unit": "г"}
                ]
            }
        )

        assert response.status_code == 401

    def test_create_recipe_with_valid_data_returns_201(self, client):
        """Создание с валидными данными должно возвращать 201"""
        response = client.post(
            "/api/v1/recipe/recipes/",
            json={
                "name_recipe": "Борщ",
                "description": "Вкусный украинский борщ",
                "ingredients": [
                    {"ingredient": "Свекла", "quantity": "300", "unit": "г"}
                ]
            },
            headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name_recipe"] == "Борщ"
        assert "id" in data
        assert "ingredients" in data

    def test_create_recipe_with_short_title_returns_422(self, client):
        """Слишком короткое название — 422"""
        response = client.post(
            "/api/v1/recipe/recipes/",
            json={
                "name_recipe": "",
                "description": "Вкусный борщ",
                "ingredients": []
            },
            headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 422

    def test_create_recipe_with_short_description_returns_422(self, client):
        """Слишком короткое описание — 422"""
        response = client.post(
            "/api/v1/recipe/recipes/",
            json={
                "name_recipe": "Борщ",
                "description": "Борщ",  # Менее 10 символов
                "ingredients": []
            },
            headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 422

    def test_create_recipe_with_invalid_token_returns_401(self, client, mock_user_service_client):
        """Невалидный токен — 401"""
        # Настраиваем мок на возврат invalid
        mock_user_service_client.validate_token.return_value = {
            "valid": False,
            "error": "Token expired"
        }

        response = client.post(
            "/api/v1/recipe/recipes/",
            json={
                "name_recipe": "Борщ",
                "description": "Вкусный украинский борщ",
                "ingredients": []
            },
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401

    def test_create_recipe_missing_required_field_returns_422(self, client):
        """Отсутствие обязательного поля — 422"""
        response = client.post(
            "/api/v1/recipe/recipes/",
            json={
                "name_recipe": "Борщ"
                # Отсутствует description
            },
            headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 422

    def test_create_recipe_with_empty_ingredients_returns_201(self, client):
        """Создание рецепта без ингредиентов — 201"""
        response = client.post(
            "/api/v1/recipe/recipes/",
            json={
                "name_recipe": "Чай",
                "description": "Просто чай",
                "ingredients": []
            },
            headers={"Authorization": "Bearer valid_token"}
        )

        assert response.status_code == 201
