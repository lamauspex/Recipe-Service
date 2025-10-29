"""
Файл конфигурации pytest
"""
import pytest
import os
from fastapi.testclient import TestClient

from main import app
from backend.services.user_service.src.database.connection import get_db
from tests.test_config import (
    TestingSessionLocal,
    create_test_tables,
    drop_test_tables,
    cleanup_test_data,
    override_get_db,
    create_test_user,
    create_test_tokens
)


@pytest.fixture(scope="session")
def setup_test_database():
    """Настройка тестовой базы данных для всей сессии тестов"""
    # Удаляем файл базы данных если он существует
    db_path = os.path.join(os.getcwd(), "test.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            # Файл заблокирован, пропускаем удаление
            pass

    # Создаем таблицы перед всеми тестами
    create_test_tables()
    yield
    # Удаляем таблицы и файл базы данных после всех тестов
    drop_test_tables()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            # Файл заблокирован, пропускаем удаление
            pass


@pytest.fixture(scope="function")
def db_session(setup_test_database):
    """Фикстура для тестовой сессии базы данных"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        cleanup_test_data(session)
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для тестового клиента"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Фикстура для создания тестового пользователя"""
    return create_test_user(db_session)


@pytest.fixture(scope="function")
def test_admin_user(db_session):
    """Фикстура для создания тестового администратора"""
    return create_test_user(
        db_session,
        username="adminuser",
        email="admin@example.com",
        is_admin=True
    )


@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Фикстура для аутентифицированного клиента"""
    with TestingSessionLocal() as db:
        access_token, _ = create_test_tokens(db, test_user)

    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client
    # Удаляем заголовок после использования
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


@pytest.fixture(scope="function")
def admin_client(client, test_admin_user):
    """Фикстура для клиента с правами администратора"""
    with TestingSessionLocal() as db:
        access_token, _ = create_test_tokens(db, test_admin_user)

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
