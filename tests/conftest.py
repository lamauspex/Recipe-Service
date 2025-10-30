"""
Файл конфигурации pytest
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.models import BaseModel
from backend.services.user_service.src.models import User, RefreshToken
from backend.services.user_service.src.services.user_service import UserService
from backend.services.user_service.src.schemas import UserCreate
from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.services.auth_service import AuthService


# Создаем тестовую базу данных в памяти
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="session")
def setup_test_database():
    """Настройка тестовой базы данных для всей сессии тестов"""
    # Создаем таблицы перед всеми тестами
    BaseModel.metadata.create_all(bind=test_engine)
    yield
    # Удаляем таблицы после всех тестов
    BaseModel.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(setup_test_database):
    """Фикстура для тестовой сессии базы данных"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        # Очищаем данные между тестами
        session.query(RefreshToken).delete()
        session.query(User).delete()
        session.commit()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для тестового клиента"""
    # Создаем минимальное приложение для тестов
    app = FastAPI(title="Test App")
    app.include_router(router)

    # Переопределяем зависимость базы данных
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Сессия закрывается в фикстуре db_session

    app.dependency_overrides[
        backend.services.user_service.src.database.connection.get_db
    ] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def test_user(db_session):
    """Фикстура для создания тестового пользователя"""
    user_service = UserService(db_session)
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )

    return user_service.create_user(user_data)


@pytest.fixture(scope="function")
def test_admin_user(db_session):
    """Фикстура для создания тестового администратора"""
    user_service = UserService(db_session)
    user_data = UserCreate(
        username="adminuser",
        email="admin@example.com",
        password="adminpassword123",
        full_name="Admin User"
    )

    user = user_service.create_user(user_data)
    user.is_admin = True
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Фикстура для аутентифицированного клиента"""
    auth_service = AuthService(client.app.dependency_overrides[
        backend.services.user_service.src.database.connection.get_db
    ]())

    access_token, _ = auth_service.create_tokens(test_user)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client

    # Удаляем заголовок после использования
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


@pytest.fixture(scope="function")
def admin_client(client, test_admin_user):
    """Фикстура для клиента с правами администратора"""
    auth_service = AuthService(client.app.dependency_overrides[
        backend.services.user_service.src.database.connection.get_db
    ]())

    access_token, _ = auth_service.create_tokens(test_admin_user)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client

    # Удаляем заголовок после использования
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


# Параметры для pytest
def pytest_configure(config):
    """Конфигурация pytest"""
    # Добавляем маркеры для тестов
    config.addinivalue_line(
        "markers", "unit: unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: integration tests"
    )
    config.addinivalue_line(
        "markers", "auth: authentication tests"
    )
    config.addinivalue_line(
        "markers", "admin: admin tests"
    )
