""" Фикстуры для тестовых данных пользователя """


import pytest

from backend.services.user_service.src.schemas import UserCreate
from backend.services.user_service.src.services.user_service import UserService
from backend.services.user_service.src.services.auth_service import AuthService


def create_test_user(
    db_session,
    username="testuser",
    email="test@example.com",
    password="Testpassword123",
    is_admin=False
):
    """Создание тестового пользователя"""
    user_service = UserService(db_session)
    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
        full_name="Test User"
    )

    user = user_service.create_user(user_data)
    if is_admin:
        user.is_admin = True
        db_session.commit()
        db_session.refresh(user)

    return user


def create_test_tokens(db_session, user):
    """Создание тестовых токенов для пользователя"""
    auth_service = AuthService(db_session)
    access_token, refresh_token = auth_service.create_tokens(user)
    return access_token, refresh_token


@pytest.fixture(scope="function")
def test_user(db_session):
    """Фикстура для создания тестового пользователя"""
    return create_test_user(
        db_session,
        username="testuser",
        email="test@example.com",
        password="Testpassword123"
    )


@pytest.fixture
def test_user_data():
    """Тестовые данные пользователя"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Testpassword123"
    }


@pytest.fixture
def user_data():
    """Тестовые данные для создания пользователя"""
    return UserCreate(
        username="testuser",
        email="test@example.com",
        password="Testpassword123",
        full_name="Test User",
    )


@pytest.fixture(scope="function")
def test_admin_user(db_session):
    """Фикстура для создания тестового администратора"""
    return create_test_user(
        db_session,
        username="adminuser",
        email="admin@example.com",
        password="Adminpassword123",
        is_admin=True
    )
