"""
Тесты для user-service
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from backend.services.user_service.src.models import RefreshToken
from backend.services.user_service.src.database.connection import get_db
from backend.services.user_service.src.models import Base

# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override для зависимости базы данных"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Создание тестовой базы данных
Base.metadata.create_all(bind=engine)

client = TestClient(app)


class TestUserAPI:
    """Тесты API пользователя"""

    def test_health_check(self):
        """Тест health check"""
        response = client.get("/api/v1/users/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "user-service"
        assert "status" in data

    def test_register_user(self):
        """Тест регистрации пользователя"""
        # Очистка базы перед тестом
        with TestingSessionLocal() as db:
            db.query(Base.metadata.tables['users']).delete()
            db.query(Base.metadata.tables['refresh_tokens']).delete()
            db.commit()

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_register_duplicate_user(self):
        """Тест регистрации дублирующего пользователя"""
        # Очистка базы перед тестом
        with TestingSessionLocal() as db:
            db.query(Base.metadata.tables['users']).delete()
            db.query(Base.metadata.tables['refresh_tokens']).delete()
            db.commit()

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        # Первый пользователь
        client.post("/api/v1/users/register", json=user_data)

        # Дублирующий пользователь
        response = client.post("/api/v1/users/register", json=user_data)
        assert response.status_code == 400

    def test_login_user(self):
        """Тест входа пользователя"""
        # Очистка базы перед тестом
        with TestingSessionLocal() as db:
            db.query(Base.metadata.tables['users']).delete()
            db.query(Base.metadata.tables['refresh_tokens']).delete()
            db.commit()

        # Сначала регистрируем пользователя
        user_data = {
            "username": "logintest",
            "email": "login@example.com",
            "password": "testpassword123"
        }
        client.post("/api/v1/users/register", json=user_data)

        # Входим
        login_data = {
            "username": "logintest",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Тест входа с неверными данными"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 401

    def test_get_current_user(self):
        """Тест получения текущего пользователя"""
        # Очистка базы перед тестом
        with TestingSessionLocal() as db:
            db.query(Base.metadata.tables['users']).delete()
            db.query(Base.metadata.tables['refresh_tokens']).delete()
            db.commit()

        # Регистрация и вход
        user_data = {
            "username": "currentuser",
            "email": "current@example.com",
            "password": "testpassword123"
        }
        client.post("/api/v1/users/register", json=user_data)

        login_data = {
            "username": "currentuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/users/login", json=login_data)
        token = login_response.json()["access_token"]

        # Получение текущего пользователя
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "currentuser"

    def test_update_current_user(self):
        """Тест обновления текущего пользователя"""
        # Очистка базы перед тестом
        with TestingSessionLocal() as db:
            db.query(Base.metadata.tables['users']).delete()
            db.query(Base.metadata.tables['refresh_tokens']).delete()
            db.commit()

        # Регистрация и вход
        user_data = {
            "username": "updateuser",
            "email": "update@example.com",
            "password": "testpassword123",
            "full_name": "Original Name"
        }
        client.post("/api/v1/users/register", json=user_data)

        login_data = {
            "username": "updateuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/users/login", json=login_data)
        token = login_response.json()["access_token"]

        # Обновление пользователя
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio"
        }
        response = client.put("/api/v1/users/me",
                              json=update_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["bio"] == "Updated bio"

    def test_refresh_token(self):
        """Тест обновления токена"""
        # Очистка базы перед тестом
        with TestingSessionLocal() as db:
            db.query(Base.metadata.tables['users']).delete()
            db.query(Base.metadata.tables['refresh_tokens']).delete()
            db.commit()

        # Регистрация и вход
        user_data = {
            "username": "refreshuser",
            "email": "refresh@example.com",
            "password": "testpassword123"
        }
        client.post("/api/v1/users/register", json=user_data)

        login_data = {
            "username": "refreshuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/users/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]

        # Небольшая задержка для создания токена
        import time
        time.sleep(0.2)  # Увеличим задержку

        # Проверяем, что токен создан в базе
        with TestingSessionLocal() as db:
            token_record = db.query(RefreshToken).filter(
                RefreshToken.token == refresh_token
            ).first()
            print(f"Token exists in DB: {token_record is not None}")
            if token_record:
                print(f"Token revoked: {token_record.is_revoked}")
                print(f"Token expires: {token_record.expires_at}")

        # Обновление токена
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/users/refresh", json=refresh_data)
        print(f"Refresh response status: {response.status_code}")
        print(f"Refresh response: {response.text}")

        if response.status_code != 200:
            # Проверяем состояние токена в базе
            with TestingSessionLocal() as db:
                token_record = db.query(RefreshToken).filter(
                    RefreshToken.token == refresh_token
                ).first()
                if token_record:
                    print(f"Token revoked: {token_record.is_revoked}")
                else:
                    print("Token not found in DB")

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_logout(self):
        """Тест выхода из системы"""
        # Очистка базы перед тестом
        with TestingSessionLocal() as db:
            db.query(Base.metadata.tables['users']).delete()
            db.query(Base.metadata.tables['refresh_tokens']).delete()
            db.commit()

        # Регистрация и вход
        user_data = {
            "username": "logoutuser",
            "email": "logout@example.com",
            "password": "testpassword123"
        }
        client.post("/api/v1/users/register", json=user_data)

        login_data = {
            "username": "logoutuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/v1/users/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]

        # Выход
        logout_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/users/logout", json=logout_data)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Успешный выход из системы"


if __name__ == "__main__":
    pytest.main([__file__])
