""" Тесты API register_user.py """

from user_service.models import User


class TestUserApi:
    """Класс тестов для API пользователей"""

    def test_register_new_user(self, client, db_session):
        """Тест регистрации нового пользователя"""

        data = {
            "user_name": "jon",
            "email": "jonsll@example.com",
            "password": "Rewlj695mnnrfv5"
        }
        response = client.post(
            "/api/v1/auth/auth_users/register",
            json=data
        )

        assert response.status_code == 200
        assert response.json().get("user_name") == "jon"

    def test_unique_user_name_constraint(self, client, db_session):
        """Тест ограничения на уникальное имя пользователя"""

        data = {
            "user_name": "menko",
            "email": "amendf@example.com",
            "password": "UniquePassw0rd"
        }
        response = client.post(
            "/api/v1/auth/auth_users/register",
            json=data
        )

        assert response.status_code == 200

        # Попытка создать пользователя с тем же username
        duplicate_data = {
            "user_name": "menko",  # Тот же username!
            "email": "another@example.com",
            "password": "AnotherPassw0rd"
        }
        response = client.post(
            "/api/v1/auth/auth_users/register",
            json=duplicate_data
        )
        assert response.status_code != 200  # Должна вернуть ошибку

    def test_minimal_registration(self, client, db_session):
        """Тест отката транзакции при ошибке"""

        # Пробуем зарегистрировать пользователя с пустым именем
        data = {
            "user_name": "",
            "email": "invalid@example.com",
            "password": "InvalidPassw0rd"
        }
        response = client.post(
            "/api/v1/auth/auth_users/register",
            json=data
        )
        assert response.status_code != 200

        # Проверяем отсутствие пользователя в базе
        users = db_session.query(User).all()
        assert len(users) == 0

    def test_required_fields_validation(self, client, db_session):
        """Тест контроля обязательных полей при регистрации"""

        missing_field_data = {
            "user_name": "missing_field",
            "email": ""
        }
        response = client.post(
            "/api/v1/auth/auth_users/register",
            json=missing_field_data
        )

        assert response.status_code != 200
        assert "Ошибка валидации" in response.text or \
            "VALIDATION_ERROR" in response.text
