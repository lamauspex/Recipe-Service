"""
Фикстуры для тестовых данных рецептов
"""

import pytest

from backend.services.recipe_service.src.services.recipe_service import (
    RecipeService)
from backend.services.recipe_service.src.schemas import (
    RecipeCreate, RecipeUpdate)
from backend.services.recipe_service.src.models import (
    Recipe, Ingredient, RecipeStep, Category, Rating)


@pytest.fixture
def recipe_service(db_session):
    """Фикстура для RecipeService"""
    return RecipeService(db_session)


@pytest.fixture
def sample_recipe_data():
    """Тестовые данные рецепта"""
    return {
        "title": "Тестовый рецепт пасты",
        "description": "Простой и вкусный рецепт пасты",
        "cooking_time": 30,
        "difficulty": "medium",
        "servings": 4,
    }


@pytest.fixture
def recipe_create_data():
    """Тестовые данные для создания рецепта"""
    return RecipeCreate(
        title="Тестовый рецепт",
        description="Описание тестового рецепта",
        ingredients=["ингредиент 1", "ингредиент 2"],
        instructions=["Шаг 1. Приготовить\nШаг 2. Подать"],
        cooking_time=30,
        difficulty="easy",
        servings=2
    )


@pytest.fixture
def recipe_update_data():
    """Тестовые данные для обновления рецепта"""
    return RecipeUpdate(
        title="Обновленный рецепт",
        description="Обновленное описание",
        ingredients=["новый ингредиент 1", "новый ингредиент 2"],
        instructions=["Обновленный шаг 1", "Обновленный шаг 2"],
        cooking_time=45,
        difficulty="сложно",
        servings=3
    )


@pytest.fixture
def test_recipe(db_session, test_user):
    """Фикстура для создания тестового рецепта"""
    recipe = {
        "title": "Тестовый рецепт",
        "description": "Тестовое описание",
        "ingredients": ["тест1", "тест2"],
        "instructions": "тест инструкция",
        "cooking_time": 30,
        "difficulty": "easy",
        "servings": 2,
        "author_id": str(test_user.id),
        "is_published": True
    }

    recipe = Recipe(**recipe)
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)

    # Добавляем ингредиенты
    ingredient1 = Ingredient(
        recipe_id=recipe.id,
        name="ингредиент 1",
        quantity="100г"
    )
    ingredient2 = Ingredient(
        recipe_id=recipe.id,
        name="ингредиент 2",
        quantity="2шт"
    )
    db_session.add_all([ingredient1, ingredient2])

    # Добавляем шаги
    step1 = RecipeStep(
        recipe_id=recipe.id,
        step_number=1,
        description="Шаг 1 приготовления"
    )
    step2 = RecipeStep(
        recipe_id=recipe.id,
        step_number=2,
        description="Шаг 2 приготовления"
    )
    db_session.add_all([step1, step2])

    db_session.commit()
    db_session.refresh(recipe)

    return recipe


@pytest.fixture
def test_category(db_session):
    """Фикстура для создания тестовой категории"""
    category = Category(
        name="Тестовая категория",
        description="Описание тестовой категории"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_rating(db_session, test_recipe, test_user):
    """Фикстура для создания тестового рейтинга"""
    rating = Rating(
        recipe_id=test_recipe.id,
        user_id=test_user.id,
        value=5,
        comment="Отличный рецепт!"
    )
    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)
    return rating


# Утилитные функции для тестов рецептов
def create_test_recipe(db_session, author, **kwargs):
    """Создание тестового рецепта"""
    default_data = {
        "title": "Тестовый рецепт",
        "description": "Тестовое описание рецепта",
        "cooking_time": 30,
        "difficulty": "средне",
        "servings": 4,
        "author_id": str(author.id)
    }
    default_data.update(kwargs)

    recipe = Recipe(**default_data)
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe


def create_test_ingredients(db_session, recipe, ingredients_data):
    """Создание тестовых ингредиентов"""
    ingredients = []
    for i, name in enumerate(ingredients_data):
        ingredient = Ingredient(
            recipe_id=recipe.id,
            name=name,
            quantity=f"{(i+1)*100}г"
        )
        ingredients.append(ingredient)

    db_session.add_all(ingredients)
    db_session.commit()
    return ingredients


def create_test_steps(db_session, recipe, steps_data):
    """Создание тестовых шагов"""
    steps = []
    for i, description in enumerate(steps_data, 1):
        step = RecipeStep(
            recipe_id=recipe.id,
            step_number=i,
            description=description
        )
        steps.append(step)

    db_session.add_all(steps)
    db_session.commit()
    return steps
