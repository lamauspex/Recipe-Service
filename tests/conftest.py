"""
Конфигурация фикстур для всех тестов
"""

import os
import pytest
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
    create_engine, event, inspect,
    Table, Column, String, MetaData
)

from backend.services.user_service.src.models import (
    RefreshToken, User, Base as UserBase)
from backend.services.recipe_service.src.models import (
    Recipe, Ingredient, RecipeStep, Category,
    RecipeCategory, Rating, Base as RecipeBase)


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


# Создаем mock таблицу categories для тестов
def create_mock_categories_table():
    """Создает временную таблицу categories для тестов"""
    metadata = MetaData()

    categories_table = Table(
        'categories', metadata,
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column('name', String(100), nullable=False),
        Column('description', String(255))
    )

    categories_table.create(bind=test_engine, checkfirst=True)


@pytest.fixture(scope="session")
def setup_test_database():
    """Настройка тестовой базы данных для всей сессии тестов"""
    # Создаем таблицы перед всеми тестами
    UserBase.metadata.create_all(bind=test_engine)
    RecipeBase.metadata.create_all(bind=test_engine)

    yield
    # Удаляем таблицы после всех тестов
    UserBase.metadata.drop_all(bind=test_engine)
    RecipeBase.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(setup_test_database):
    """Фикстура для тестовой сессии базы данных"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Очищаем данные между тестами
        cleanup_test_data(session)


def cleanup_test_data(db_session):
    """Очистка тестовых данных между тестами"""
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
        if inspector.has_table('refresh_tokens'):
            db_session.query(RefreshToken).delete()
        if inspector.has_table('users'):
            db_session.query(User).delete()
        db_session.commit()

    except Exception as e:
        db_session.rollback()
        raise e
