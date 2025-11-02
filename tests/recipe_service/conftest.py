"""
Конфигурация фикстур для recipe_service тестов
"""

import os
import pytest
from dotenv import load_dotenv
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    create_engine, event, inspect
)

from tests.user_service.fixtures.user_fixtures import *
from tests.user_service.fixtures.client_fixtures import *
from tests.recipe_service.fixtures.recipe_fixtures import *
from tests.recipe_service.fixtures.client_fixtures import *
from backend.services.recipe_service.src.models import (
    Recipe, Ingredient, RecipeStep, Category, RecipeCategory,
    Rating, Base as RecipeBase
)

# Загружаем переменные окружения из .env файла
load_dotenv()


# Настройки тестовой базы данных (отдельная для recipe-service)
TEST_DATABASE_PATH = os.path.join(os.getcwd(), "test.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"

# Движок базы данных для recipe тестов
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# Фабрика сессий для тестов
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


# Настройка поддержки UUID и внешних ключей для SQLite
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


@pytest.fixture(scope="session")
def setup_test_database():
    """Настройка тестовой базы данных для recipe-service"""
    # Создаем таблицы recipe-service перед всеми тестами
    RecipeBase.metadata.create_all(bind=test_engine)

    yield
    # Удаляем таблицы после всех тестов
    RecipeBase.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(setup_test_database):
    """Фикстура для тестовой сессии базы данных recipe-service"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Очищаем данные между тестами
        cleanup_test_data(session)


def cleanup_test_data(db_session):
    """Очистка тестовых данных recipe-service между тестами"""
    try:
        db_session.rollback()
        inspector = inspect(db_session.bind)

        # Очищаем в правильном порядке из-за внешних ключей
        if inspector.has_table('ratings'):
            db_session.query(Rating).delete()
        if inspector.has_table('recipe_steps'):
            db_session.query(RecipeStep).delete()
        if inspector.has_table('ingredients'):
            db_session.query(Ingredient).delete()
        if inspector.has_table('recipe_categories'):
            db_session.query(RecipeCategory).delete()
        if inspector.has_table('categories'):
            db_session.query(Category).delete()
        if inspector.has_table('recipes'):
            db_session.query(Recipe).delete()

        db_session.commit()

    except Exception as e:
        db_session.rollback()
        raise e


# Дополнительные фикстуры для recipe-service тестов
@pytest.fixture(scope="function")
def test_user_with_recipes(db_session, test_user):
    """Фикстура: пользователь с несколькими рецептами"""
    # Создаем несколько рецептов для пользователя
    recipe1 = create_test_recipe(
        db_session,
        test_user,
        title="Рецепт 1",
        difficulty="легко"
    )
    recipe2 = create_test_recipe(
        db_session,
        test_user,
        title="Рецепт 2",
        difficulty="средне"
    )

    return {
        "user": test_user,
        "recipes": [recipe1, recipe2]
    }


@pytest.fixture(scope="function")
def populated_recipe_data(db_session, test_user):
    """Фикстура: база данных с рецептами и данными"""
    # Создаем рецепт с ингредиентами и шагами
    recipe = create_test_recipe(db_session, test_user)
    ingredients = create_test_ingredients(
        db_session, recipe, ["мука", "яйца", "молоко"]
    )
    steps = create_test_steps(
        db_session, recipe, ["Смешать ингредиенты", "Выпекать 30 минут"]
    )

    return {
        "recipe": recipe,
        "ingredients": ingredients,
        "steps": steps
    }
