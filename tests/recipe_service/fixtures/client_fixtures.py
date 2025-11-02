import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.services.recipe_service.src.api.recipe_router import router
from backend.services.recipe_service.src.database.connection import get_db
from backend.services.user_service.src.services.auth_service import AuthService


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для тестового клиента"""
    app = FastAPI(title="Test Recipe App")
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
def auth_headers(client, test_user):
    """Фикстура для заголовков аутентификации"""
    # Получаем доступ к базе данных через override
    db_session = client.app.dependency_overrides[get_db]()
    auth_service = AuthService(db_session)
    access_token, _ = auth_service.create_tokens(test_user)

    return {"Authorization": f"Bearer {access_token}"}
