"""
Тесты для middleware user-service
"""

from uuid import UUID
from datetime import timedelta

from backend.services.user_service.src.services.auth_service import AuthService
from tests.user_service.fixtures.client_fixtures import *
from tests.user_service.fixtures.user_fixtures import (
    create_test_user,
    create_test_tokens
)


def test_jwt_middleware_valid_token(client, db_session):
    """Тест JWT middleware с валидным токеном"""
    # Создаем тестового пользователя
    user = create_test_user(
        db_session,
        user_name="test-user",
        email="test@example.com"
    )
    access_token, _ = create_test_tokens(db_session, user)

    # Запрос с валидным токеном
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] == "test-user"
    # Проверяем, что ID является UUID
    UUID(data["id"])


def test_jwt_middleware_invalid_token(client):
    """Тест JWT middleware с невалидным токеном"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 401


def test_jwt_middleware_no_token(client):
    """Тест JWT middleware без токена"""
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_jwt_middleware_expired_token(client, db_session):
    """Тест JWT middleware с просроченным токеном"""
    # Создаем просроченный токен напрямую через сервис
    auth_service = AuthService(db_session)
    user = create_test_user(
        db_session,
        user_name="testuser",
        email="test@example.com"
    )

    # Создаем токен с коротким сроком действия
    expired_token = auth_service.create_access_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(seconds=1)
    )

    # Ждем истечения срока действия
    import time
    time.sleep(2)

    # Попытка использовать просроченный токен
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 401


def test_admin_middleware_admin_user(client, db_session):
    """Тест admin middleware для администратора"""
    # Создаем администратора
    admin_user = create_test_user(
        db_session,
        user_name="adminuser",
        email="admin@example.com",
        is_admin=True
    )
    access_token, _ = create_test_tokens(db_session, admin_user)

    # Запрос с токеном администратора
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/users/", headers=headers)

    assert response.status_code == 200


def test_admin_middleware_regular_user(client, db_session):
    """Тест admin middleware для обычного пользователя"""
    # Создаем обычного пользователя
    regular_user = create_test_user(
        db_session,
        user_name="regularuser",
        email="regular@example.com"
    )
    access_token, _ = create_test_tokens(db_session, regular_user)

    # Попытка доступа к админскому эндпоинту
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/users/", headers=headers)

    assert response.status_code == 403


def test_exception_handler_validation_error(client):
    """Тест обработчика исключений валидации"""
    # Отправка невалидных данных
    invalid_data = {
        "user_name": "",            # Пустой user_name
        "email": "invalid-email",  # Невалидный email
        "password": "123"          # Слишком короткий пароль
    }
    response = client.post(
        "/api/v1/users/register", json=invalid_data)

    assert response.status_code == 422
    data = response.json()
    # Проверяем стандартную структуру ответа FastAPI
    assert "detail" in data


def test_exception_handler_not_found(client, db_session):
    """Тест обработчика исключений для несуществующего ресурса"""
    # Создаем администратора
    admin_user = create_test_user(
        db_session,
        user_name="testuser",
        email="test@example.com",
        is_admin=True
    )
    access_token, _ = create_test_tokens(db_session, admin_user)

    # Попытка получить несуществующего пользователя
    headers = {"Authorization": f"Bearer {access_token}"}
    fake_uuid = "12345678-1234-5678-1234-567812345678"
    response = client.get(
        f"/api/v1/users/{fake_uuid}",
        headers=headers
    )

    assert response.status_code == 404
    data = response.json()
    # Проверяем стандартную структуру ответа FastAPI
    assert "detail" in data
