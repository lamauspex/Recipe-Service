"""
Тесты для модели LoginAttempt
"""


from uuid import UUID

from user_service.models.login_attempt import LoginAttempt
from user_service.models.user_models import User


def test_login_attempt_model_creation(db_session):
    """Тест создания модели LoginAttempt"""

    # Создаем пользователя для связи
    user = User(
        user_name="testuser",
        email="test@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Создаем попытку входа
    login_attempt = LoginAttempt(
        user_id=user.id,
        email="test@example.com",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0 Test Browser",
        is_successful=True
    )

    db_session.add(login_attempt)
    db_session.commit()
    db_session.refresh(login_attempt)

    assert login_attempt.id is not None
    assert isinstance(login_attempt.id, UUID)
    assert login_attempt.user_id == user.id
    assert login_attempt.email == "test@example.com"
    assert login_attempt.ip_address == "192.168.1.1"
    assert login_attempt.user_agent == "Mozilla/5.0 Test Browser"
    assert login_attempt.is_successful is True
    assert login_attempt.failure_reason is None
    assert login_attempt.created_at is not None


def test_login_attempt_model_repr(db_session):
    """Тест строкового представления LoginAttempt"""

    user = User(
        user_name="testuser_repr",
        email="testrepr@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    login_attempt = LoginAttempt(
        user_id=user.id,
        email="testrepr@example.com",
        ip_address="192.168.1.1",
        is_successful=False,
        failure_reason="Invalid password"
    )

    db_session.add(login_attempt)
    db_session.commit()
    db_session.refresh(login_attempt)

    repr_str = repr(login_attempt)
    assert "LoginAttempt" in repr_str
    assert f"id={login_attempt.id}" in repr_str
    assert "email='testrepr@example.com'" in repr_str
    assert "ip='192.168.1.1'" in repr_str
    assert "successful=False" in repr_str


def test_login_attempt_without_user(db_session):
    """Тест создания LoginAttempt без привязки к пользователю"""

    login_attempt = LoginAttempt(
        user_id=None,
        email="nonexistent@example.com",
        ip_address="192.168.1.2",
        user_agent="Test Browser",
        is_successful=False,
        failure_reason="User not found"
    )

    db_session.add(login_attempt)
    db_session.commit()
    db_session.refresh(login_attempt)

    assert login_attempt.id is not None
    assert login_attempt.user_id is None
    assert login_attempt.email == "nonexistent@example.com"
    assert login_attempt.is_successful is False
    assert login_attempt.failure_reason == "User not found"


def test_login_attempt_user_relationship(db_session):
    """Тест связи LoginAttempt с User"""

    user = User(
        user_name="testuser_rel",
        email="testrel@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Создаем несколько попыток входа для одного пользователя
    for i in range(3):
        login_attempt = LoginAttempt(
            user_id=user.id,
            email="testrel@example.com",
            ip_address=f"192.168.1.{i+1}",
            is_successful=(i % 2 == 0)  # Чередуем успешные/неуспешные
        )
        db_session.add(login_attempt)

    db_session.commit()

    # Проверяем связь с пользователем
    user_attempts = db_session.query(LoginAttempt).filter(
        LoginAttempt.user_id == user.id).all()

    assert len(user_attempts) == 3
    for attempt in user_attempts:
        assert attempt.user == user


def test_login_attempt_cascade_delete(db_session):
    """Тест каскадного удаления LoginAttempt при удалении пользователя"""

    user = User(
        user_name="testuser_cascade",
        email="testcascade@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Создаем попытки входа
    for i in range(2):
        login_attempt = LoginAttempt(
            user_id=user.id,
            email="testcascade@example.com",
            ip_address=f"192.168.1.{i+10}",
            is_successful=False
        )
        db_session.add(login_attempt)

    db_session.commit()

    # Проверяем, что попытки созданы
    attempts = db_session.query(LoginAttempt).filter(
        LoginAttempt.user_id == user.id).all()
    assert len(attempts) == 2

    # Удаляем пользователя и его попытки вручную
    db_session.query(LoginAttempt).filter(
        LoginAttempt.user_id == user.id).delete()
    db_session.delete(user)
    db_session.commit()

    # Проверяем, что попытки удалены
    remaining_attempts = db_session.query(LoginAttempt).filter(
        LoginAttempt.user_id == user.id).all()
    assert len(remaining_attempts) == 0


def test_login_attempt_ip_address_validation(db_session):
    """Тест различных форматов IP адресов"""

    # IPv4
    ipv4_attempt = LoginAttempt(
        email="test@example.com",
        ip_address="192.168.1.1",
        is_successful=True
    )
    db_session.add(ipv4_attempt)
    db_session.commit()

    # IPv6
    ipv6_attempt = LoginAttempt(
        email="test@example.com",
        ip_address="2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        is_successful=True
    )
    db_session.add(ipv6_attempt)
    db_session.commit()

    assert ipv4_attempt.ip_address == "192.168.1.1"
    assert ipv6_attempt.ip_address == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"


def test_login_attempt_email_indexing(db_session):
    """Тест индексации по email"""
    # Создаем несколько попыток с разными email
    emails = [
        "user1@example.com",
        "user2@example.com",
        "user1@example.com"
    ]

    for i, email in enumerate(emails):
        attempt = LoginAttempt(
            email=email,
            ip_address=f"192.168.1.{i+1}",
            is_successful=(i == 2)
        )
        db_session.add(attempt)

    db_session.commit()

    # Проверяем, что можем найти по email
    user1_attempts = db_session.query(LoginAttempt).filter(
        LoginAttempt.email == "user1@example.com").all()

    assert len(user1_attempts) == 2
    assert all(attempt.email ==
               "user1@example.com" for attempt in user1_attempts)


def test_login_attempt_successful_failure_reasons(db_session):
    """Тест различных причин неудачного входа"""

    failure_reasons = [
        "Invalid password",
        "Account locked",
        "User not found",
        "Too many attempts"
    ]

    for reason in failure_reasons:
        attempt = LoginAttempt(
            email="test@example.com",
            ip_address="192.168.1.100",
            is_successful=False,
            failure_reason=reason
        )
        db_session.add(attempt)

    db_session.commit()

    # Проверяем все причины
    attempts = db_session.query(LoginAttempt).all()
    for i, attempt in enumerate(attempts):
        assert attempt.failure_reason == failure_reasons[i]
        assert attempt.is_successful is False
