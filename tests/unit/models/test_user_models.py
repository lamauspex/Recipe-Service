"""
Тесты для моделей user-service
"""

from backend.services.user_service.src.models import User, RefreshToken
from uuid import UUID
from datetime import datetime, timezone, timedelta
import pytest


def test_user_model_creation(db_session):
    """Тест создания модели пользователя"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password123",
        full_name="Test User",
        bio="Test bio",
        is_active=True,
        is_admin=False
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert isinstance(user.id, UUID)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password123"
    assert user.full_name == "Test User"
    assert user.bio == "Test bio"
    assert user.is_active is True
    assert user.is_admin is False
    assert user.created_at is not None
    assert isinstance(user.created_at, datetime)


def test_user_model_repr(db_session):
    """Тест строкового представления пользователя"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password123"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    repr_str = repr(user)
    assert "User" in repr_str
    assert f"id={user.id}" in repr_str
    assert "username='testuser'" in repr_str
    assert "email='test@example.com'" in repr_str


def test_user_model_unique_constraints(db_session):
    """Тест уникальных ограничений пользователя"""
    # Первый пользователь
    user1 = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user1)
    db_session.commit()

    # Второй пользователь с таким же username
    user2 = User(
        username="testuser",  # Дубликат
        email="test2@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user2)

    with pytest.raises(Exception):  # Должна быть ошибка уникальности
        db_session.commit()

    db_session.rollback()

    # Третий пользователь с таким же email
    user3 = User(
        username="testuser2",
        email="test@example.com",  # Дубликат
        hashed_password="hashed_password123"
    )
    db_session.add(user3)

    with pytest.raises(Exception):  # Должна быть ошибка уникальности
        db_session.commit()


def test_refresh_token_model_creation(db_session):
    """Тест создания модели refresh токена"""
    # Сначала создаем пользователя
    user = User(
        username="testuser_token",
        email="testtoken@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Создаем токен
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    token = RefreshToken(
        user_id=user.id,
        token="test_refresh_token_123",
        expires_at=expires_at
    )

    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)

    assert token.id is not None
    assert isinstance(token.id, UUID)
    assert token.user_id == user.id
    assert token.token == "test_refresh_token_123"
    assert token.is_revoked is False
    assert token.created_at is not None
    # Сравниваем с учетом возможной разницы в timezone
    assert token.expires_at.replace(
        tzinfo=None) == expires_at.replace(tzinfo=None)


def test_refresh_token_model_repr(db_session):
    """Тест строкового представления refresh токена"""
    user = User(
        username="testuser_repr",
        email="testrepr@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = RefreshToken(
        user_id=user.id,
        token="test_refresh_token_repr",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )

    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)

    repr_str = repr(token)
    assert "RefreshToken" in repr_str
    assert f"id={token.id}" in repr_str
    assert f"user_id={user.id}" in repr_str


def test_refresh_token_unique_constraint(db_session):
    """Тест уникальности токена"""
    user = User(
        username="testuser_unique",
        email="testunique@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Первый токен
    token1 = RefreshToken(
        user_id=user.id,
        token="same_token",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db_session.add(token1)
    db_session.commit()

    # Второй токен с таким же значением
    token2 = RefreshToken(
        user_id=user.id,
        token="same_token",  # Дубликат
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db_session.add(token2)

    with pytest.raises(Exception):  # Должна быть ошибка уникальности
        db_session.commit()


def test_cascade_delete_user_tokens(db_session):
    """Тест каскадного удаления токенов при удалении пользователя"""
    user = User(
        username="testuser_cascade",
        email="testcascade@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Создаем несколько токенов
    for i in range(3):
        token = RefreshToken(
            user_id=user.id,
            token=f"token_{i}",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(token)

    db_session.commit()

    # Проверяем, что токены созданы
    tokens = db_session.query(RefreshToken).filter(
        RefreshToken.user_id == user.id).all()
    assert len(tokens) == 3

    # Удаляем пользователя и его токены вручную
    db_session.query(RefreshToken).filter(
        RefreshToken.user_id == user.id).delete()
    db_session.delete(user)
    db_session.commit()

    # Проверяем, что токены удалены
    tokens = db_session.query(RefreshToken).filter(
        RefreshToken.user_id == user.id).all()
    assert len(tokens) == 0
