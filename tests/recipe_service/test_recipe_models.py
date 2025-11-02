
"""
Тесты для моделей recipe-service
"""


from datetime import datetime
from uuid import UUID

from backend.services.recipe_service.src.models import (
    Recipe, Ingredient, RecipeStep, Category, Rating
)


def test_recipe_model_creation(db_session, test_user):
    """Тест создания модели рецепта"""
    recipe = Recipe(
        title="Тестовый рецепт",
        description="Описание тестового рецепта",
        cooking_time=30,
        difficulty="средне",
        servings=4,
        author_id=str(test_user.id)
    )

    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)

    assert recipe.id is not None
    assert isinstance(recipe.id, UUID)
    assert recipe.title == "Тестовый рецепт"
    assert recipe.cooking_time == 30
    assert recipe.difficulty == "средне"
    assert recipe.servings == 4
    assert recipe.author_id == str(test_user.id)
    assert recipe.created_at is not None
    assert isinstance(recipe.created_at, datetime)


def test_ingredient_model_creation(db_session, test_recipe):
    """Тест создания модели ингредиента"""
    ingredient = Ingredient(
        recipe_id=test_recipe.id,
        name="Тестовый ингредиент",
        quantity="100г"
    )

    db_session.add(ingredient)
    db_session.commit()
    db_session.refresh(ingredient)

    assert ingredient.id is not None
    assert ingredient.recipe_id == test_recipe.id
    assert ingredient.name == "Тестовый ингредиент"
    assert ingredient.quantity == "100г"


def test_recipe_step_model_creation(db_session, test_recipe):
    """Тест создания модели шага рецепта"""
    step = RecipeStep(
        recipe_id=test_recipe.id,
        step_number=1,
        description="Тестовый шаг"
    )

    db_session.add(step)
    db_session.commit()
    db_session.refresh(step)

    assert step.id is not None
    assert step.recipe_id == test_recipe.id
    assert step.step_number == 1
    assert step.description == "Тестовый шаг"


def test_category_model_creation(db_session):
    """Тест создания модели категории"""
    category = Category(
        name="Тестовая категория",
        description="Описание категории"
    )

    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    assert category.id is not None
    assert category.name == "Тестовая категория"
    assert category.description == "Описание категории"


def test_rating_model_creation(db_session, test_recipe, test_user):
    """Тест создания модели рейтинга"""
    rating = Rating(
        recipe_id=test_recipe.id,
        user_id=test_user.id,
        value=5,
        comment="Отличный рецепт!"
    )

    db_session.add(rating)
    db_session.commit()
    db_session.refresh(rating)

    assert rating.id is not None
    assert rating.recipe_id == test_recipe.id
    assert rating.user_id == test_user.id
    assert rating.value == 5
    assert rating.comment == "Отличный рецепт!"


def test_recipe_relationships(db_session, test_user):
    """Тест связей рецепта с ингредиентами и шагами"""
    # Создаем рецепт
    recipe = Recipe(
        title="Тестовый рецепт",
        description="Описание",
        cooking_time=30,
        difficulty="легко",
        servings=2,
        author_id=str(test_user.id)
    )
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
        quantity="200г"
    )
    db_session.add_all([ingredient1, ingredient2])

    # Добавляем шаги
    step1 = RecipeStep(
        recipe_id=recipe.id,
        step_number=1,
        description="Шаг 1"
    )
    step2 = RecipeStep(
        recipe_id=recipe.id,
        step_number=2,
        description="Шаг 2"
    )
    db_session.add_all([step1, step2])

    db_session.commit()
    db_session.refresh(recipe)

    # Проверяем связи
    assert len(recipe.ingredients) == 2
    assert len(recipe.steps) == 2
    assert recipe.ingredients[0].name == "ингредиент 1"
    assert recipe.steps[0].step_number == 1
