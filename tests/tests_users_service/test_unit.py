"""
Тесты валидаторов
Тесты исключений
"""


from backend.service_user.src.exception import (
    AppException,
    InvalidCredentialsException,
    TokenExpiredException
)
from backend.service_user.src.schemas import (
    EmailValidator,
    NameValidator,
    PasswordSchemaValidator
)


class TestEmailValidator:
    """Тесты EmailValidator"""

    def test_valid_email_returns_true(self, valid_email: str):
        """Валидный email должен проходить валидацию"""
        is_valid, errors = EmailValidator.validate(valid_email)

        assert is_valid is True
        assert len(errors) == 0

    def test_invalid_email_returns_false(self, invalid_email: str):
        """Невалидный email должен возвращать ошибку"""
        is_valid, errors = EmailValidator.validate(invalid_email)

        assert is_valid is False
        assert len(errors) > 0

    def test_email_normalize(self, valid_email: str):
        """Email должен нормализовываться к нижнему регистру"""
        normalized = EmailValidator.normalize("TEST@EXAMPLE.COM")

        assert normalized == "test@example.com"


class TestPasswordValidator:
    """Тесты PasswordSchemaValidator"""

    def test_valid_password_returns_true(self, valid_password: str):
        """Валидный пароль должен проходить валидацию"""
        is_valid, errors = PasswordSchemaValidator.validate(valid_password)

        assert is_valid is True
        assert len(errors) == 0

    def test_weak_password_returns_false(self, weak_password: str):
        """Слабый пароль (common password) должен возвращать ошибку"""
        is_valid, errors = PasswordSchemaValidator.validate(weak_password)

        assert is_valid is False
        assert "Пароль слишком простой" in errors


class TestNameValidator:
    """Тесты NameValidator"""

    def test_valid_name_returns_true(self, valid_name: str):
        """Валидное имя пользователя должно проходить валидацию"""
        is_valid, errors = NameValidator.validate(valid_name)

        assert is_valid is True
        assert len(errors) == 0

    def test_short_name_returns_false(self, short_name: str):
        """Слишком короткое имя должно возвращать ошибку"""
        is_valid, errors = NameValidator.validate(short_name)

        assert is_valid is False
        assert len(errors) > 0


class TestAppException:
    """Тесты базового исключения AppException"""

    def test_app_exception_to_dict(self):
        """Исключение должно сериализоваться в словарь"""
        exc = AppException(
            message="Test error",
            status_code=400,
            code="TEST_ERROR"
        )

        result = exc.to_dict()

        assert result["error"]["message"] == "Test error"
        assert result["error"]["status_code"] == 400
        assert result["error"]["code"] == "TEST_ERROR"

    def test_app_exception_with_details(self):
        """Исключение с дополнительными деталями"""
        exc = AppException(
            message="Validation failed",
            status_code=422,
            code="VALIDATION_ERROR",
            details={
                "field": "email",
                "reason": "invalid"
            }
        )

        result = exc.to_dict()

        assert result["error"]["details"]["field"] == "email"


class TestInvalidCredentialsException:
    """Тесты InvalidCredentialsException"""

    def test_default_message(self):
        """Проверка сообщения по умолчанию"""
        exc = InvalidCredentialsException()

        assert exc.status_code == 401
        assert exc.code == "INVALID_CREDENTIALS"

    def test_custom_message(self):
        """Кастомное сообщение"""
        exc = InvalidCredentialsException(message="Wrong password")

        assert exc.message == "Wrong password"


class TestTokenExpiredException:
    """Тесты TokenExpiredException"""

    def test_default_message(self):
        """Проверка сообщения по умолчанию"""
        exc = TokenExpiredException()

        assert exc.status_code == 401
        assert exc.code == "TOKEN_EXPIRED"
