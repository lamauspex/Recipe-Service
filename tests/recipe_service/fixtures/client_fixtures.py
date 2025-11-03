"""
Фикстуры для тестового клиента и аутентификации
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.services.recipe_service.main import app
from backend.services.recipe_service.src.database.connection import get_db
from backend.services.user_service.src.services.auth_service import AuthService


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для тестового клиента с тестовой базой данных"""
    # Перехватываем зависимость get_db для использования тестовой сессии
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with patch(
        'backend.services.recipe_service.src.database.connection.get_db',
        override_get_db
    ):
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture(scope="function")
def auth_headers(test_user, db_session):
    """Фикстура для заголовков аутентификации с реальным JWT токеном"""
    # Используем тестовую сессию базы данных
    auth_service = AuthService(db_session)

    # Создаем JWT токен для тестового пользователя
    access_token = auth_service.create_access_token(
        data={"sub": test_user.user_name}
    )

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
