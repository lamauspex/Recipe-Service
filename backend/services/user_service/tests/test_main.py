"""
Тесты для user-service
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database.connection import get_db, Base

# Тестовая база данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint(client: TestClient):
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "User Service is running"


def test_health_endpoint(client: TestClient):
    """Тест эндпоинта health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user(client: TestClient):
    """Тест регистрации пользователя"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/users/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"


def test_register_duplicate_user(client: TestClient):
    """Тест регистрации пользователя с дубликатом"""
    user_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpass123"
    }
    # Регистрация первого пользователя
    client.post("/api/v1/users/register", json=user_data)
    
    # Попытка регистрации с тем же email
    duplicate_data = user_data.copy()
    duplicate_data["username"] = "testuser3"
    response = client.post("/api/v1/users/register", json=duplicate_data)
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]


def test_login_user(client: TestClient):
    """Тест входа пользователя"""
    # Сначала зарегистрируем пользователя
    user_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "loginpass123"
    }
    client.post("/api/v1/users/register", json=user_data)
    
    # Входим
    login_data = {
        "username": "loginuser",
        "password": "loginpass123"
    }
    response = client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_login_wrong_credentials(client: TestClient):
    """Тест входа с неверными данными"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpass"
    }
    response = client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 401
    assert "Неверное имя пользователя или пароль" in response.json()["detail"]