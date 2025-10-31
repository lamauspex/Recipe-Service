import pytest
from backend.services.user_service.src.services.user_service import UserService
from backend.services.user_service.src.services.auth_service import AuthService


@pytest.fixture
def user_service(db_session):
    """Фикстура для UserService"""
    return UserService(db_session)


@pytest.fixture
def auth_service(db_session):
    """Фикстура для AuthService"""
    return AuthService(db_session)
