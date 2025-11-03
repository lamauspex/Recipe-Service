"""
Фикстуры для тестового клиента
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.services.user_service.src.api.routes import router
from backend.services.user_service.src.database.connection import get_db
from backend.services.user_service.src.services.auth_service import AuthService


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для тестового клиента"""
    app = FastAPI(title="Test App")
    app.include_router(router)

    # Перехватываем базу данных для тестов
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def authenticated_client(client, test_user):
    """Фикстура для аутентифицированного клиента"""
    auth_service = AuthService(client.app.dependency_overrides[get_db]())
    access_token, _ = auth_service.create_tokens(test_user)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client

    # Remove header after use
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


@pytest.fixture(scope="function")
def admin_client(client, test_admin_user):
    """Фикстура для клиента с правами администратора"""
    auth_service = AuthService(client.app.dependency_overrides[get_db]())
    access_token, _ = auth_service.create_tokens(test_admin_user)
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    yield client

    # Remove header after use
    if "Authorization" in client.headers:
        del client.headers["Authorization"]
