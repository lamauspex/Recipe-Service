"""
Тесты для сервисного слоя user-service
"""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from backend.services.user_service.src.services.user_service import UserService
from backend.services.user_service.src.schemas import UserCreate, UserUpdate
from tests.fixtures.service_fixtures import *
from tests.fixtures.user_fixtures import *


def test_password_hashing(auth_service):
    """Тест хеширования пароля"""
    password = "test_password_123"
    hashed = auth_service.get_password_hash(password)

    # Проверяем, что хеш отличается от пароля
    assert hashed != password
    assert len(hashed) > 50  # Argon2 хеш должен быть длинным

    # Проверяем, что пароль верифицируется правильно
    assert auth_service.verify_password(password, hashed) is True
    assert auth_service.verify_password("wrong_password", hashed) is False


def test_password_hashing_too_long(auth_service):
    """Тест хеширования слишком длинного пароля"""
    long_password = "a" * 1025  # 1025 символов
    with pytest.raises(ValueError, match="Пароль слишком длинный"):
        auth_service.get_password_hash(long_password)


def test_create_access_token(auth_service):
    """Тест создания access token"""
    data = {"sub": "testuser"}
    token = auth_service.create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 100  # JWT токен должен быть длинным

    # Проверяем, что токен верифицируется
    payload = auth_service.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "jti" in payload


def test_create_access_token_with_expiry(auth_service):
    """Тест создания access token с自定义 сроком действия"""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=5)
    token = auth_service.create_access_token(data, expires_delta)

    payload = auth_service.verify_token(token)
    assert payload is not None

    # Проверяем, что срок действия установлен правильно
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected_time = datetime.now(timezone.utc) + expires_delta

    # Разница должна быть небольшой (меньше секунды)
    time_diff = abs((exp_time - expected_time).total_seconds())
    assert time_diff < 1


def test_create_refresh_token(auth_service):
    """Тест создания refresh token"""
    data = {"sub": "testuser", "user_id": str(uuid4())}
    token = auth_service.create_refresh_token(data)

    assert isinstance(token, str)
    assert len(token) > 100

    payload = auth_service.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["type"] == "refresh"
    assert "user_id" in payload
    assert "exp" in payload
    assert "jti" in payload


def test_verify_invalid_token(auth_service):
    """Тест верификации невалидного токена"""
    invalid_tokens = [
        "invalid.token.here",
        "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ0ZXN0In0.invalid",
        "",
        "not_a_token_at_all"
    ]

    for token in invalid_tokens:
        payload = auth_service.verify_token(token)
        assert payload is None


def test_verify_expired_token(auth_service):
    """Тест верификации просроченного токена"""
    data = {"sub": "testuser"}
    # Создаем токен с отрицательным сроком действия (уже просроченный)
    token = auth_service.create_access_token(
        data,
        expires_delta=timedelta(seconds=-1)
    )

    payload = auth_service.verify_token(token)
    assert payload is None


def test_authenticate_user_success(auth_service, test_user_data):
    """Тест успешной аутентификации пользователя"""
    # Создаем пользователя через сервис
    user_service = UserService(auth_service.db)
    user_create = UserCreate(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password=test_user_data["password"],
        full_name="Test User"
    )
    user = user_service.create_user(user_create)

    # Аутентифицируем пользователя
    authenticated_user = auth_service.authenticate_user(
        test_user_data["username"],
        test_user_data["password"]
    )

    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    assert authenticated_user.username == user.username


def test_authenticate_user_wrong_password(auth_service, test_user_data):
    """Тест аутентификации с неверным паролем"""
    # Создаем пользователя
    user_service = UserService(auth_service.db)
    user_create = UserCreate(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password=test_user_data["password"],
        full_name="Test User"
    )
    user_service.create_user(user_create)

    # Пытаемся аутентифицироваться с неверным паролем
    authenticated_user = auth_service.authenticate_user(
        test_user_data["username"],
        "wrong_password"
    )

    assert authenticated_user is None


def test_authenticate_user_not_exists(auth_service):
    """Тест аутентификации несуществующего пользователя"""
    authenticated_user = auth_service.authenticate_user(
        "nonexistent_user",
        "some_password"
    )

    assert authenticated_user is None


def test_create_tokens(auth_service, test_user_data):
    """Тест создания пары токенов"""
    # Создаем пользователя
    user_service = UserService(auth_service.db)
    user_create = UserCreate(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password=test_user_data["password"],
        full_name="Test User"
    )
    user = user_service.create_user(user_create)

    # Создаем токены
    access_token, refresh_token = auth_service.create_tokens(user)

    # Проверяем access token
    access_payload = auth_service.verify_token(access_token)
    assert access_payload is not None
    assert access_payload["sub"] == user.username
    assert access_payload["type"] == "access"

    # Проверяем refresh token
    refresh_payload = auth_service.verify_token(refresh_token)
    assert refresh_payload is not None
    assert refresh_payload["sub"] == user.username
    assert refresh_payload["type"] == "refresh"
    assert refresh_payload["user_id"] == str(user.id)

    # Проверяем, что refresh токен сохранен в базе
    saved_token = auth_service.refresh_token_repo.get_valid_token(
        refresh_token)
    assert saved_token is not None
    assert saved_token.user_id == user.id
    assert saved_token.token == refresh_token


def test_revoke_refresh_token(auth_service):
    """Тест отзыва refresh token"""
    # Создаем тестового пользователя
    user_service = UserService(auth_service.db)
    user_create = UserCreate(
        username="testuser_token",
        email="token@example.com",
        password="Testpassword123",
        full_name="Test User"
    )
    user = user_service.create_user(user_create)

    # Создаем токены для пользователя
    access_token, refresh_token = auth_service.create_tokens(user)

    # Проверяем, что токен существует
    saved_token = auth_service.refresh_token_repo.get_valid_token(
        refresh_token)
    assert saved_token is not None
    assert saved_token.is_revoked is False

    # Отзываем токен
    success = auth_service.revoke_refresh_token(refresh_token)
    assert success is True

    # Проверяем, что токен отозван
    revoked_token = auth_service.refresh_token_repo.get_valid_token(
        refresh_token)
    assert revoked_token is None

    # Проверяем, что повторный отзыв того же токена тоже возвращает True
    # (токен находится, но уже отозван - метод все равно возвращает True)
    success = auth_service.revoke_refresh_token(refresh_token)
    assert success is True


def test_get_user_from_token(auth_service, test_user_data):
    """Тест получения пользователя из токена"""
    # Создаем пользователя
    user_service = UserService(auth_service.db)
    user_create = UserCreate(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password=test_user_data["password"],
        full_name="Test User"
    )
    user = user_service.create_user(user_create)

    # Создаем токен
    _, refresh_token = auth_service.create_tokens(user)

    # Получаем пользователя из токена
    user_from_token = auth_service.get_user_from_token(refresh_token)
    assert user_from_token is not None
    assert user_from_token.id == user.id
    assert user_from_token.username == user.username


def test_get_user_from_invalid_token(auth_service):
    """Тест получения пользователя из невалидного токена"""
    user_from_token = auth_service.get_user_from_token("invalid_token")
    assert user_from_token is None


def test_create_user(user_service, user_data):
    """Тест создания пользователя"""
    user = user_service.create_user(user_data)

    assert user is not None
    assert user.username == user_data.username
    assert user.email == user_data.email
    assert user.full_name == user_data.full_name
    assert user.is_active is True
    assert user.is_admin is False
    assert user.hashed_password is not None
    assert user.hashed_password != user_data.password


def test_get_user_by_id(user_service, user_data):
    """Тест получения пользователя по ID"""
    # Создаем пользователя
    created_user = user_service.create_user(user_data)

    # Получаем пользователя по ID
    found_user = user_service.get_user(created_user.id)

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.username == created_user.username


def test_get_user_by_username(user_service, user_data):
    """Тест получения пользователя по username"""
    # Создаем пользователя
    created_user = user_service.create_user(user_data)

    # Получаем пользователя по username
    found_user = user_service.get_user_by_username(created_user.username)

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.username == created_user.username


def test_get_user_by_email(user_service, user_data):
    """Тест получения пользователя по email"""
    # Создаем пользователя
    created_user = user_service.create_user(user_data)

    # Получаем пользователя по email
    found_user = user_service.get_user_by_email(created_user.email)

    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.email == created_user.email


def test_update_user(user_service, user_data):
    """Тест обновления пользователя"""
    # Создаем пользователя
    created_user = user_service.create_user(user_data)

    # Обновляем данные
    update_data = UserUpdate(
        full_name="Updated Name",
        bio="Updated bio"
    )
    updated_user = user_service.update_user(created_user.id, update_data)

    assert updated_user is not None
    assert updated_user.full_name == "Updated Name"
    assert updated_user.bio == "Updated bio"
    # Проверяем, что другие поля не изменились
    assert updated_user.username == created_user.username
    assert updated_user.email == created_user.email


def test_update_user_with_dict(user_service, user_data):
    """Тест обновления пользователя с передачей dict"""
    # Создаем пользователя
    created_user = user_service.create_user(user_data)

    # Обновляем данные через dict
    update_data = {
        "full_name": "Dict Updated Name",
        "bio": "Dict updated bio"
    }
    updated_user = user_service.update_user(created_user.id, update_data)

    assert updated_user is not None
    assert updated_user.full_name == "Dict Updated Name"
    assert updated_user.bio == "Dict updated bio"


def test_update_user_email_conflict(user_service, user_data):
    """Тест обновления пользователя с конфликтом email"""
    # Создаем двух пользователей
    user1 = user_service.create_user(user_data)

    user2_data = UserCreate(
        username="testuser2",
        email="test2@example.com",
        password="Testpassword123",
        full_name="Test User 2"
    )
    user2 = user_service.create_user(user2_data)

    # Пытаемся обновить email пользователя2 на email пользователя1
    update_data = UserUpdate(email=user1.email)

    with pytest.raises(
        ValueError,
        match="Пользователь с таким email уже существует"
    ):
        user_service.update_user(user2.id, update_data)


def test_delete_user(user_service, user_data):
    """Тест удаления пользователя"""
    # Создаем пользователя
    created_user = user_service.create_user(user_data)

    # Удаляем пользователя
    success = user_service.delete_user(created_user.id)
    assert success is True

    # Проверяем, что пользователь удален
    deleted_user = user_service.get_user(created_user.id)
    assert deleted_user is None


def test_get_users(user_service, user_data):
    """Тест получения списка пользователей"""
    # Создаем несколько пользователей
    users = []
    for i in range(3):
        user_data_i = UserCreate(
            username=f"testuser{i}",
            email=f"test{i}@example.com",
            password="Testpassword123",
            full_name=f"Test User {i}"
        )
        users.append(user_service.create_user(user_data_i))

    # Получаем список пользователей
    all_users = user_service.get_users()

    assert len(all_users) >= 3
    usernames = [user.username for user in all_users]
    for i in range(3):
        assert f"testuser{i}" in usernames


def test_get_users_with_pagination(user_service, user_data):
    """Тест получения списка пользователей с пагинацией"""
    # Создаем несколько пользователей
    users = []
    for i in range(5):
        user_data_i = UserCreate(
            username=f"testuser{i}",
            email=f"test{i}@example.com",
            password="Yestpassword123",
            full_name=f"Test User {i}"
        )
        users.append(user_service.create_user(user_data_i))

    # Получаем пользователей с пагинацией
    page1 = user_service.get_users(skip=0, limit=2)
    page2 = user_service.get_users(skip=2, limit=2)

    assert len(page1) == 2
    assert len(page2) == 2
    # Проверяем, что это разные пользователи
    page1_ids = {user.id for user in page1}
    page2_ids = {user.id for user in page2}
    assert len(page1_ids.intersection(page2_ids)) == 0


def test_get_active_users(user_service, user_data):
    """Тест получения списка активных пользователей"""
    # Создаем пользователя
    user = user_service.create_user(user_data)

    # Получаем активных пользователей
    active_users = user_service.get_active_users()

    assert len(active_users) >= 1
    user_ids = [u.id for u in active_users]
    assert user.id in user_ids


def test_activate_user(user_service, user_data):
    """Тест активации пользователя"""
    # Создаем пользователя
    user = user_service.create_user(user_data)

    # Деактивируем сначала
    user_service.deactivate_user(user.id)

    # Активируем пользователя
    activated_user = user_service.activate_user(user.id)

    assert activated_user is not None
    assert activated_user.is_active is True


def test_deactivate_user(user_service, user_data):
    """Тест деактивации пользователя"""
    # Создаем пользователя
    user = user_service.create_user(user_data)

    # Деактивируем пользователя
    deactivated_user = user_service.deactivate_user(user.id)

    assert deactivated_user is not None
    assert deactivated_user.is_active is False


def test_set_admin(user_service, user_data):
    """Тест установки прав администратора"""
    # Создаем пользователя
    user = user_service.create_user(user_data)

    # Делаем пользователя администратором
    admin_user = user_service.set_admin(user.id, is_admin=True)

    assert admin_user is not None
    assert admin_user.is_admin is True

    # Убираем права администратора
    regular_user = user_service.set_admin(user.id, is_admin=False)

    assert regular_user is not None
    assert regular_user.is_admin is False


def test_get_nonexistent_user(user_service):
    """Тест получения несуществующего пользователя"""
    fake_uuid = uuid4()
    user = user_service.get_user(fake_uuid)
    assert user is None


def test_get_nonexistent_user_by_username(user_service):
    """Тест получения несуществующего пользователя по username"""
    user = user_service.get_user_by_username("nonexistent_user")
    assert user is None


def test_get_nonexistent_user_by_email(user_service):
    """Тест получения несуществующего пользователя по email"""
    user = user_service.get_user_by_email("nonexistent@example.com")
    assert user is None


def test_update_nonexistent_user(user_service):
    """Тест обновления несуществующего пользователя"""
    fake_uuid = uuid4()
    update_data = UserUpdate(full_name="Updated Name")

    updated_user = user_service.update_user(fake_uuid, update_data)
    assert updated_user is None


def test_delete_nonexistent_user(user_service):
    """Тест удаления несуществующего пользователя"""
    fake_uuid = uuid4()
    success = user_service.delete_user(fake_uuid)
    assert success is False
