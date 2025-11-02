
"""
Тесты для RecipeService
"""

import pytest
from uuid import uuid4
from fastapi import HTTPException

from backend.services.recipe_service.src.schemas import (
    RecipeCreate, RecipeUpdate, RecipeSearchParams
)
from tests.fixtures.recipe_fixtures import *
from tests.user_service.fixtures.user_fixtures import *


def test_create_recipe_success(self, recipe_service, test_user):
    """Тест успешного создания рецепта"""
    recipe_data = RecipeCreate(
        title="Новый рецепт",
        description="Описание нового рецепта",
        ingredients=["ингредиент 1", "ингредиент 2"],
        instructions=["Шаг 1", "Шаг 2"],
        cooking_time=30,
        difficulty="легко",
        servings=2
    )

    recipe = recipe_service.create_recipe(recipe_data, test_user.id)

    assert recipe.id is not None
    assert recipe.title == "Новый рецепт"
    assert recipe.author_id == test_user.id
    assert len(recipe.ingredients) == 2
    assert len(recipe.instructions) == 2


def test_get_recipe_success(self, recipe_service, test_recipe):
    """Тест успешного получения рецепта"""
    recipe = recipe_service.get_recipe(test_recipe.id)

    assert recipe.id == test_recipe.id
    assert recipe.title == test_recipe.title


def test_get_recipe_not_found(self, recipe_service):
    """Тест получения несуществующего рецепта"""
    fake_id = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        recipe_service.get_recipe(fake_id)

    assert exc_info.value.status_code == 404
    assert "Рецепт не найден" in exc_info.value.detail


def test_update_recipe_success(self,
                               recipe_service,
                               test_recipe,
                               test_user):
    """Тест успешного обновления рецепта"""
    update_data = RecipeUpdate(
        title="Обновленный рецепт",
        description="Обновленное описание"
    )

    updated_recipe = recipe_service.update_recipe(
        test_recipe.id, update_data, test_user.id
    )

    assert updated_recipe.title == "Обновленный рецепт"
    assert updated_recipe.description == "Обновленное описание"


def test_update_recipe_not_found(self, recipe_service, test_user):
    """Тест обновления несуществующего рецепта"""
    fake_id = uuid4()
    update_data = RecipeUpdate(title="Обновленный рецепт")

    with pytest.raises(HTTPException) as exc_info:
        recipe_service.update_recipe(fake_id, update_data, test_user.id)

    assert exc_info.value.status_code == 404


def test_update_recipe_no_permission(self, recipe_service, test_recipe):
    """Тест обновления рецепта без прав"""
    other_user_id = uuid4()
    update_data = RecipeUpdate(title="Обновленный рецепт")

    with pytest.raises(HTTPException) as exc_info:
        recipe_service.update_recipe(
            test_recipe.id, update_data, other_user_id)

    assert exc_info.value.status_code == 403
    assert "Недостаточно прав" in exc_info.value.detail


def test_delete_recipe_success(self,
                               recipe_service,
                               test_recipe,
                               test_user):
    """Тест успешного удаления рецепта"""
    result = recipe_service.delete_recipe(test_recipe.id, test_user.id)

    assert result is True


def test_delete_recipe_not_found(self, recipe_service, test_user):
    """Тест удаления несуществующего рецепта"""
    fake_id = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        recipe_service.delete_recipe(fake_id, test_user.id)

    assert exc_info.value.status_code == 404


def test_get_recipes_list(self, recipe_service, test_recipe):
    """Тест получения списка рецептов"""

    search_params = RecipeSearchParams(skip=0, limit=10)
    recipes = recipe_service.get_recipes_list(search_params)

    assert len(recipes) >= 1
    assert any(r.id == test_recipe.id for r in recipes)
