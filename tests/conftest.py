"""
Глобальные фикстуры для pytest
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from user_service.config import settings
from user_service.database import database
from user_service.models.base_models import Base, BaseModel
from main import app_users


class TestBaseModel(BaseModel):
    """Тестовая модель для проверки базового функционала миксинов"""

    __tablename__ = "test_models"
    __test__ = False

    name: str = "test_field"


@pytest.fixture(scope="function")
def engine():
    """Создает тестовую базу данных SQLite в памяти для каждого теста"""

    # Используем тестовый URL из настроек
    if settings.database.TESTING:
        database_url = "sqlite:///:memory:"
    else:
        database_url = settings.database.get_database_url("sqlite")

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Создаем все таблицы
    Base.metadata.create_all(engine)

    yield engine

    # Очищаем после теста
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Создает сессию базы данных для каждого теста"""

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture(scope="function")
def client(engine, db_session):
    """Создает тестового клиента FastAPI"""

    # Переопределяем зависимость get_db
    def override_get_db():
        yield db_session

    app_users.dependency_overrides[database.get_db] = override_get_db

    # Также обновляем engine в database менеджере для прямых обращений
    original_engine = database.engine
    original_session_local = database.SessionLocal

    database.engine = engine
    database.SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    try:
        with TestClient(app_users) as test_client:
            yield test_client
    finally:
        # Восстанавливаем оригинальные значения
        app_users.dependency_overrides.clear()
        database.engine = original_engine
        database.SessionLocal = original_session_local
