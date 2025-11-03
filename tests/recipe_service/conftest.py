"""
Конфигурация фикстур для recipe_service тестов
"""
import os
import pytest
from dotenv import load_dotenv
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    create_engine, event, inspect, text
)
from fastapi.testclient import TestClient
from unittest.mock import patch


from tests.user_service.fixtures.user_fixtures import *
from tests.recipe_service.fixtures.recipe_fixtures import (
    create_test_recipe, create_test_ingredients, create_test_steps,
    create_test_category, create_test_rating, get_sample_recipe_data,
    get_recipe_create_data, get_recipe_update_data
)
from backend.services.recipe_service.src.services.recipe_service import (
    RecipeService
)
from backend.services.user_service.src.services.auth_service import AuthService
from backend.services.user_service.models.token_models import RefreshToken
from backend.services.user_service.models.user_models import User
from backend.services.recipe_service.models import (
    Base, Recipe, Rating, Ingredient,
    Category, RecipeCategory, RecipeStep
)


# Устанавливаем переменную окружения для тестов ПЕРЕД импортами
os.environ["TESTING"] = "true"


# Импортируем функции из фикстур

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройки тестовой базы данных
TEST_DATABASE_PATH = os.path.join(os.getcwd(), "test.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"

# Движок базы данных для тестов
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


@pytest.fixture(scope="function")
def client():
    """Фикстура для тестового клиента FastAPI с тестовой базой данных"""
    from backend.services.recipe_service.main import app

    # Создаем приложение с тестовой базой данных
    with patch('backend.services.recipe_service.src.database.connection.engine', test_engine):
        with patch('backend.services.recipe_service.src.database.connection.SessionLocal', TestingSessionLocal):
            yield TestClient(app)


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Фикстура для заголовков аутентификации с реальным JWT токеном"""
    # Используем тестовую сессию базы данных
    db_session = TestingSessionLocal()

    try:
        # Создаем сервис аутентификации
        auth_service = AuthService(db_session)

        # Генерируем JWT токен для тестового пользователя
        token = auth_service.create_access_token(
            data={"sub": test_user.user_name}
        )

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    finally:
        db_session.close()


@pytest.fixture(scope="function")
def test_recipe(db_session, test_user):
    """Фикстура для создания тестового рецепта"""
    return create_test_recipe(db_session, test_user)


@pytest.fixture(scope="function")
def recipe_service(db_session):
    """Фикстура для RecipeService"""
    return RecipeService(db_session)


@pytest.fixture(scope="function")
def test_category(db_session):
    """Фикстура для создания тестовой категории"""
    return create_test_category(db_session)


@pytest.fixture(scope="function")
def test_rating(db_session, test_recipe, test_user):
    """Фикстура для создания тестового рейтинга"""
    return create_test_rating(db_session, test_recipe, test_user)


@pytest.fixture
def sample_recipe_data():
    """Тестовые данные рецепта"""
    return get_sample_recipe_data()


@pytest.fixture
def recipe_create_data():
    """Тестовые данные для создания рецепта"""
    return get_recipe_create_data()


@pytest.fixture
def recipe_update_data():
    """Тестовые данные для обновления рецепта"""
    return get_recipe_update_data()


@pytest.fixture(scope="session")
def setup_test_database():
    """Настройка тестовой базы данных для recipe-service"""
    # Создаем таблицы user-service для фикстур
    User.metadata.create_all(bind=test_engine)

    # Создаем таблицы recipe-service перед всеми тестами
    Base.metadata.create_all(bind=test_engine)

    yield
    # Удаляем таблицы после всех тестов
    Base.metadata.drop_all(bind=test_engine)
    User.metadata.drop_all(bind=test_engine)


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

        # Отключаем внешние ключи для безопасной очистки
        db_session.execute(text("PRAGMA foreign_keys = OFF"))

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

        # Очищаем таблицы user-service
        if inspector.has_table('refresh_tokens'):
            db_session.query(RefreshToken).delete()
        if inspector.has_table('users'):
            db_session.query(User).delete()

        db_session.commit()

        # Включаем обратно внешние ключи
        db_session.execute(text("PRAGMA foreign_keys = ON"))

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
