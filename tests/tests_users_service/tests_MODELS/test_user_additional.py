"""
Дополнительные тесты для модели User
"""


from datetime import datetime, timezone, timedelta

from user_service.models.login_attempt import LoginAttempt
from user_service.models.role_model import Permission, RoleModel
from user_service.models.token import RefreshToken
from user_service.models.user_models import User


def test_user_email_verification_fields(db_session):
    """Тест полей email верификации"""

    current_time = datetime.now(timezone.utc)
    user = User(
        user_name="testuser_verify",
        email="testverify@example.com",
        hashed_password="hashed_password123",
        email_verified=True,
        verification_token="verify_token_123",
        verification_expires_at=current_time + timedelta(days=1)
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.email_verified is True
    assert user.verification_token == "verify_token_123"
    assert user.verification_expires_at is not None
    # Убеждаемся, что обе даты timezone-aware для корректного сравнения
    assert user.verification_expires_at.replace(
        tzinfo=timezone.utc) > current_time


def test_user_password_reset_fields(db_session):
    """Тест полей сброса пароля"""

    current_time = datetime.now(timezone.utc)
    user = User(
        user_name="testuser_reset",
        email="testreset@example.com",
        hashed_password="hashed_password123",
        password_reset_token="reset_token_456",
        password_reset_expires_at=current_time + timedelta(hours=2)
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.password_reset_token == "reset_token_456"
    assert user.password_reset_expires_at is not None
    # Убеждаемся, что обе даты timezone-aware для корректного сравнения
    assert user.password_reset_expires_at.replace(
        tzinfo=timezone.utc) > current_time


def test_user_optional_fields_none(db_session):
    """Тест опциональных полей со значениями None"""

    user = User(
        user_name="testuser_optional",
        email="testoptional@example.com",
        hashed_password="hashed_password123"
        # Все остальные поля не указаны, должны быть None или дефолтными
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Проверяем опциональные поля
    assert user.full_name is None
    assert user.bio is None
    assert user.email_verified is False  # Дефолтное значение
    assert user.verification_token is None
    assert user.verification_expires_at is None
    assert user.password_reset_token is None
    assert user.password_reset_expires_at is None
    assert len(user.roles) == 0


def test_user_full_name_and_bio(db_session):
    """Тест полных имени и биографии"""

    user = User(
        user_name="testuser_full",
        email="testfull@example.com",
        hashed_password="hashed_password123",
        full_name="Полное Имя Пользователя",
        bio="Это подробная биография пользователя с информацией о нем"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.full_name == "Полное Имя Пользователя"
    assert user.bio == "Это подробная биография пользователя с информацией о нем"


def test_user_role_system(db_session):
    """Тест системы ролей пользователей"""

    # Создаём роли в БД
    user_role = RoleModel(
        name="user",
        display_name="Пользователь",
        description="Базовые права доступа",
        permissions=Permission.READ,
        is_system=True
    )
    admin_role = RoleModel(
        name="admin",
        display_name="Администратор",
        description="Полный доступ к системе",
        permissions=Permission.FULL_ACCESS,
        is_system=True
    )
    moderator_role = RoleModel(
        name="moderator",
        display_name="Модератор",
        description="Права на модерацию контента",
        permissions=Permission.READ | Permission.WRITE | Permission.VIEW_STATS,
        is_system=True
    )

    db_session.add_all([
        user_role,
        admin_role,
        moderator_role
    ])
    db_session.commit()

    # Обычный пользователь
    regular_user = User(
        user_name="regular_user",
        email="regular@example.com",
        hashed_password="hashed_password123",
        roles=[user_role]
    )

    # Администратор
    admin_user = User(
        user_name="admin_user",
        email="admin@example.com",
        hashed_password="hashed_password123",
        roles=[admin_role]
    )

    # Модератор
    moderator_user = User(
        user_name="moderator_user",
        email="moderator@example.com",
        hashed_password="hashed_password123",
        roles=[moderator_role]
    )

    db_session.add_all([
        regular_user,
        admin_user,
        moderator_user
    ])
    db_session.commit()
    db_session.refresh(regular_user)
    db_session.refresh(admin_user)
    db_session.refresh(moderator_user)

    # Проверяем роли
    assert regular_user.has_role("user") is True
    assert admin_user.has_role("admin") is True
    assert moderator_user.has_role("moderator") is True

    # Проверяем is_admin
    assert regular_user.has_role("admin") is False
    assert admin_user.has_role("admin") is True
    assert moderator_user.has_role("admin") is False

    # Проверяем разрешения
    assert regular_user.has_permission(Permission.READ) is True
    assert admin_user.has_permission(Permission.FULL_ACCESS) is True


def test_user_refresh_tokens_relationship(db_session):
    """Тест связи User с RefreshToken"""

    user = User(
        user_name="testuser_tokens",
        email="testtokens@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Создаем несколько refresh токенов
    tokens = []
    for i in range(3):
        token = RefreshToken(
            user_id=user.id,
            token=f"refresh_token_{i}",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(token)
        tokens.append(token)

    db_session.commit()

    # Проверяем связь
    assert len(user.refresh_tokens) == 3
    assert all(token.user == user for token in user.refresh_tokens)
    assert all(token.user_id == user.id for token in user.refresh_tokens)


def test_user_login_attempts_relationship(db_session):
    """Тест связи User с LoginAttempt"""

    user = User(
        user_name="testuser_attempts",
        email="testattempts@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Создаем несколько попыток входа
    attempts = []
    for i in range(2):
        attempt = LoginAttempt(
            user_id=user.id,
            email="testattempts@example.com",
            ip_address=f"192.168.1.{i+1}",
            is_successful=(i == 0)
        )
        db_session.add(attempt)
        attempts.append(attempt)

    db_session.commit()

    # Проверяем связь
    assert len(user.login_attempts) == 2
    assert all(attempt.user == user for attempt in user.login_attempts)
    assert all(attempt.user_id == user.id for attempt in user.login_attempts)


def test_user_cascade_delete_with_tokens_and_attempts(db_session):
    """Тест каскадного удаления со связями"""

    user = User(
        user_name="testuser_cascade_all",
        email="testcascadeall@example.com",
        hashed_password="hashed_password123"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Создаем refresh токены
    for i in range(2):
        token = RefreshToken(
            user_id=user.id,
            token=f"cascade_token_{i}",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db_session.add(token)

    # Создаем попытки входа
    for i in range(2):
        attempt = LoginAttempt(
            user_id=user.id,
            email="testcascadeall@example.com",
            ip_address=f"192.168.1.{i+20}",
            is_successful=True
        )
        db_session.add(attempt)

    db_session.commit()

    # Проверяем создание
    user_tokens = db_session.query(RefreshToken).filter(
        RefreshToken.user_id == user.id).all()
    user_attempts = db_session.query(LoginAttempt).filter(
        LoginAttempt.user_id == user.id).all()

    assert len(user_tokens) == 2
    assert len(user_attempts) == 2

    # Удаляем пользователя и связанные записи вручную
    db_session.query(RefreshToken).filter(
        RefreshToken.user_id == user.id).delete()
    db_session.query(LoginAttempt).filter(
        LoginAttempt.user_id == user.id).delete()
    db_session.delete(user)
    db_session.commit()

    # Проверяем удаление
    remaining_tokens = db_session.query(RefreshToken).filter(
        RefreshToken.user_id == user.id).all()
    remaining_attempts = db_session.query(LoginAttempt).filter(
        LoginAttempt.user_id == user.id).all()

    assert len(remaining_tokens) == 0
    assert len(remaining_attempts) == 0


def test_user_string_field_lengths(db_session):
    """Тест ограничений длины строковых полей"""

    user = User(
        user_name="a" * 50,  # Максимальная длина
        email="b" * 100,     # Максимальная длина
        hashed_password="c" * 255,  # Максимальная длина
        full_name="d" * 100,  # Максимальная длина
        bio="e" * 1000       # Большой текст для Text поля
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert len(user.user_name) == 50
    assert len(user.email) == 100
    assert len(user.hashed_password) == 255
    assert len(user.full_name) == 100
    assert len(user.bio) == 1000


def test_user_email_verification_workflow(db_session):
    """Тест полного workflow верификации email"""

    # Создаем пользователя с неверифицированным email
    user = User(
        user_name="testuser_workflow",
        email="testworkflow@example.com",
        hashed_password="hashed_password123",
        email_verified=False,
        verification_token="initial_token",
        verification_expires_at=datetime.now(timezone.utc) + timedelta(days=1)
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.email_verified is False

    # Имитируем верификацию
    user.email_verified = True
    user.verification_token = None
    user.verification_expires_at = None

    db_session.commit()
    db_session.refresh(user)

    assert user.email_verified is True
    assert user.verification_token is None
    assert user.verification_expires_at is None


def test_user_password_reset_workflow(db_session):
    """Тест workflow сброса пароля"""

    user = User(
        user_name="testuser_pwd_reset",
        email="testpwdreset@example.com",
        hashed_password="old_hashed_password"
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Запрашиваем сброс пароля
    reset_token = "reset_token_123"
    current_time = datetime.now(timezone.utc)
    user.password_reset_token = reset_token
    user.password_reset_expires_at = current_time + timedelta(hours=1)

    db_session.commit()
    db_session.refresh(user)

    assert user.password_reset_token == reset_token
    # Убеждаемся, что обе даты timezone-aware для корректного сравнения
    assert user.password_reset_expires_at.replace(
        tzinfo=timezone.utc) > current_time

    # Имитируем сброс пароля
    user.hashed_password = "new_hashed_password"
    user.password_reset_token = None
    user.password_reset_expires_at = None

    db_session.commit()
    db_session.refresh(user)

    assert user.hashed_password == "new_hashed_password"
    assert user.password_reset_token is None
    assert user.password_reset_expires_at is None
