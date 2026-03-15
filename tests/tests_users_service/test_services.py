"""Тесты сервисов"""

import pytest
from unittest.mock import Mock

from backend.service_user.src.core import (
    PasswordService,
    JWTService,
    AuthValidator
)


class TestPasswordService:
    """Тесты PasswordService"""

    @pytest.fixture
    def password_service(self) -> PasswordService:
        """Фикстура сервиса паролей"""
        return PasswordService()

    def test_hash_password_returns_string(
        self,
        password_service: PasswordService
    ):
        """Хеширование пароля должно возвращать строку"""
        hashed = password_service.hash_password("SecurePass123!")

        assert isinstance(hashed, str)
        assert hashed != "SecurePass123!"

    def test_verify_correct_password_returns_true(
        self,
        password_service: PasswordService
    ):
        """Проверка правильного пароля должна возвращать True"""
        password = "SecurePass123!"
        hashed = password_service.hash_password(password)

        result = password_service.verify_password(password, hashed)

        assert result is True

    def test_verify_wrong_password_returns_false(
        self,
        password_service: PasswordService
    ):
        """Проверка неправильного пароля должна возвращать False"""
        hashed = password_service.hash_password("SecurePass123!")

        result = password_service.verify_password("WrongPassword456!", hashed)

        assert result is False

    def test_hash_password_uses_argon2(
        self,
        password_service: PasswordService
    ):
        """Хеширование должно использовать Argon2"""
        hashed = password_service.hash_password("SecurePass123!")

        assert hashed.startswith("$argon2")


class TestJWTService:
    """Тесты JWTService"""

    @pytest.fixture
    def jwt_service(self) -> JWTService:
        """Фикстура JWT сервиса"""
        return JWTService(
            secret_key="test-secret-key-12345",
            algorithm="HS256",
            access_token_expire_minutes=15,
            refresh_token_expire_days=7
        )

    @pytest.fixture
    def test_payload(self) -> dict:
        """Фикстура тестовых данных"""
        return {
            "sub": "user123",
            "email": "test@example.com"
        }

    def test_create_access_token_returns_string(
        self,
        jwt_service: JWTService,
        test_payload: dict
    ):
        """Создание access токена должно возвращать строку"""
        token = jwt_service.create_access_token(test_payload)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_payload(
        self,
        jwt_service: JWTService,
        test_payload: dict
    ):
        """Access токен должен содержать переданные данные"""
        token = jwt_service.create_access_token(test_payload)
        decoded = jwt_service.decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == test_payload["sub"]
        assert decoded["type"] == "access"

    def test_create_refresh_token_returns_string(
        self,
        jwt_service: JWTService,
        test_payload: dict
    ):
        """Создание refresh токена должно возвращать строку"""
        token = jwt_service.create_refresh_token(test_payload)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_has_type_refresh(
        self,
        jwt_service: JWTService,
        test_payload: dict
    ):
        """Refresh токен должен иметь type=refresh"""
        token = jwt_service.create_refresh_token(test_payload)
        decoded = jwt_service.decode_token(token)

        assert decoded["type"] == "refresh"

    def test_decode_valid_token_returns_payload(
        self,
        jwt_service: JWTService,
        test_payload: dict
    ):
        """Декодирование валидного токена должно возвращать данные"""
        token = jwt_service.create_access_token(test_payload)
        decoded = jwt_service.decode_token(token)

        assert decoded is not None
        assert "sub" in decoded

    def test_decode_invalid_token_returns_none(
        self,
        jwt_service: JWTService
    ):
        """Декодирование невалидного токена должно возвращать None"""
        result = jwt_service.decode_token("invalid.token.here")

        assert result is None

    def test_verify_token_type_access_returns_true(
        self,
        jwt_service: JWTService,
        test_payload: dict
    ):
        """Проверка типа access токена должна возвращать True"""
        token = jwt_service.create_access_token(test_payload)

        result = jwt_service.verify_token_type(token, "access")

        assert result is True

    def test_verify_token_type_mismatch_returns_false(
        self,
        jwt_service: JWTService,
        test_payload: dict
    ):
        """Проверка неправильного типа токена должна возвращать False"""
        token = jwt_service.create_access_token(test_payload)

        result = jwt_service.verify_token_type(token, "refresh")

        assert result is False


class MockUser:
    """Mock модели пользователя для тестов"""

    def __init__(self, is_active: bool = True):
        self.is_active = is_active


class TestAuthValidator:
    """Тесты AuthValidator"""

    def test_validate_user_for_auth_none_user_returns_false(self):
        """Если пользователь None - вернуть False"""
        result = AuthValidator.validate_user_for_auth(None)

        assert result is False

    def test_validate_user_for_auth_inactive_user_returns_false(self):
        """Неактивный пользователь не может аутентифицироваться"""
        user = MockUser(is_active=False)

        result = AuthValidator.validate_user_for_auth(user)

        assert result is False

    def test_validate_user_for_auth_active_user_returns_true(self):
        """Активный пользователь может аутентифицироваться"""
        user = MockUser(is_active=True)

        result = AuthValidator.validate_user_for_auth(user)

        assert result is True

    def test_validate_password_match_returns_true(self):
        """Проверка пароля - правильный пароль"""
        password_service = Mock()
        password_service.verify_password.return_value = True

        result = AuthValidator.validate_password_match(
            "password123",
            "hashed_password",
            password_service
        )

        assert result is True
        password_service.verify_password.assert_called_once()

    def test_validate_password_match_returns_false(self):
        """Проверка пароля - неправильный пароль"""
        password_service = Mock()
        password_service.verify_password.return_value = False

        result = AuthValidator.validate_password_match(
            "wrong_password",
            "hashed_password",
            password_service
        )

        assert result is False
