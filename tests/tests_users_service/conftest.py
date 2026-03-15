"""Конфигурация pytest для user_service"""

import os
import pytest

# Устанавливаем режим тестирования
os.environ["TESTING"] = "1"
os.environ["USER_SERVICE_TESTING"] = "1"


@pytest.fixture
def valid_email() -> str:
    """Валидный email"""
    return "test@example.com"


@pytest.fixture
def invalid_email() -> str:
    """Невалидный email"""
    return "not-an-email"


@pytest.fixture
def valid_password() -> str:
    """Валидный пароль"""
    return "SecurePass123!"


@pytest.fixture
def weak_password() -> str:
    """Слабый пароль"""
    return "password"


@pytest.fixture
def short_password() -> str:
    """Короткий пароль"""
    return "Aa1!"


@pytest.fixture
def valid_name() -> str:
    """Валидное имя пользователя"""
    return "john_doe"


@pytest.fixture
def short_name() -> str:
    """Короткое имя пользователя"""
    return "ab"
