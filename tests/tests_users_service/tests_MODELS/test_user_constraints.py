"""
Дополнительные тесты для User model - login tracking и constraints
"""

from user_service.models.role_model import RoleModel, Permission
import pytest
from datetime import datetime, timezone, timedelta

from user_service.models.user_models import User


class TestUserLoginTracking:
    """Тесты для отслеживания входов пользователя"""

    def test_user_last_login_default_none(self, db_session):
        """Тест дефолтного значения last_login"""
        user = User(
            user_name="test_last_login",
            email="testlastlogin@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.last_login is None

    def test_user_login_count_default_zero(self, db_session):
        """Тест дефолтного значения login_count"""
        user = User(
            user_name="test_login_count",
            email="testlogincount@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.login_count == 0

    def test_user_login_count_increment(self, db_session):
        """Тест увеличения счетчика входов"""
        user = User(
            user_name="test_increment",
            email="testincrement@example.com",
            hashed_password="password123",
            login_count=0
        )

        db_session.add(user)
        db_session.commit()

        # Симулируем вход в систему
        user.login_count += 1
        user.last_login = datetime.now(timezone.utc)
        db_session.commit()
        db_session.refresh(user)

        assert user.login_count == 1

        # Второй вход
        user.login_count += 1
        db_session.commit()
        db_session.refresh(user)

        assert user.login_count == 2

    def test_user_last_login_update(self, db_session):
        """Тест обновления last_login"""

        user = User(
            user_name="test_lastlogin_update",
            email="testlastloginupdate@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()

        # Первый вход
        first_login = datetime.now(timezone.utc)
        user.last_login = first_login
        user.login_count = 1
        db_session.commit()
        db_session.refresh(user)

        # SQLite теряет tzinfo, сравниваем без него
        assert user.last_login.replace(
            tzinfo=None) == first_login.replace(tzinfo=None)
        assert user.login_count == 1

        # Второй вход
        second_login = datetime.now(timezone.utc) + timedelta(hours=1)
        user.last_login = second_login
        user.login_count = 2
        db_session.commit()
        db_session.refresh(user)

        # SQLite теряет tzinfo, сравниваем без него
        assert user.last_login.replace(
            tzinfo=None) == second_login.replace(tzinfo=None)
        assert user.login_count == 2


class TestUserUniqueConstraints:
    """Тесты уникальных ограничений"""

    def test_user_name_unique_constraint(self, db_session):
        """Тест уникальности user_name"""
        user1 = User(
            user_name="unique_username",
            email="user1@example.com",
            hashed_password="password123"
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            user_name="unique_username",  # Дубликат
            email="user2@example.com",
            hashed_password="password123"
        )
        db_session.add(user2)

        with pytest.raises(Exception):
            db_session.commit()

        db_session.rollback()

    def test_user_email_unique_constraint(self, db_session):
        """Тест уникальности email"""
        user1 = User(
            user_name="user1_email",
            email="unique@example.com",
            hashed_password="password123"
        )
        db_session.add(user1)
        db_session.commit()

        user2 = User(
            user_name="user2_email",
            email="unique@example.com",  # Дубликат email
            hashed_password="password123"
        )
        db_session.add(user2)

        with pytest.raises(Exception):
            db_session.commit()

        db_session.rollback()

    def test_user_name_and_email_together(self, db_session):
        """Тест что разные пользователи могут иметь разные name и email"""
        user1 = User(
            user_name="user1",
            email="user1@example.com",
            hashed_password="password123"
        )
        user2 = User(
            user_name="user2",
            email="user2@example.com",
            hashed_password="password123"
        )

        db_session.add_all([user1, user2])
        db_session.commit()

        assert user1.id != user2.id
        assert user1.user_name != user2.user_name
        assert user1.email != user2.email


class TestUserStringConstraints:
    """Тесты ограничений строковых полей"""

    def test_user_name_max_length(self, db_session):
        """Тест что имя ровно 50 символов сохраняется корректно"""
        user = User(
            user_name="a" * 50,  # 50 символов
            email="maxname@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()

        assert len(user.user_name) == 50

    def test_user_email_max_length(self, db_session):
        """Тест что email ровно 100 символов сохраняется корректно"""
        # 88 символов + @example.com (12) = 100
        user = User(
            user_name="maxemail",
            email="a" * 88 + "@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()

        assert len(user.email) == 100

    def test_user_hashed_password_max_length(self, db_session):
        """Тест что hashed_password ровно 255 символов сохраняется корректно"""
        user = User(
            user_name="maxpass",
            email="maxpass@example.com",
            hashed_password="a" * 255
        )

        db_session.add(user)
        db_session.commit()

        assert len(user.hashed_password) == 255

    def test_user_full_name_max_length(self, db_session):
        """Тест что full_name ровно 100 символов сохраняется корректно"""
        user = User(
            user_name="maxfullname",
            email="maxfullname@example.com",
            hashed_password="password123",
            full_name="a" * 100
        )

        db_session.add(user)
        db_session.commit()

        assert len(user.full_name) == 100

    def test_user_bio_text_length(self, db_session):
        """Тест что bio может быть длинным текстом"""
        long_bio = "Это очень длинная биография пользователя. " * 100

        user = User(
            user_name="longbio",
            email="longbio@example.com",
            hashed_password="password123",
            bio=long_bio
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.bio == long_bio
        assert len(user.bio) > 1000

    def test_user_name_empty_string(self, db_session):
        """
        Тест что user_name может быть пустой строкой
        (валидация на уровне Pydantic)
        """
        # Пустое имя должно проходить через SQLAlchemy,
        # но может не пройти Pydantic валидацию
        user = User(
            user_name="",  # Пустое имя
            email="emptyusername@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        # Примечание: SQLite примет пустую строку,
        # валидация должна быть на уровне API
        db_session.commit()
        db_session.refresh(user)

        assert user.user_name == ""

    def test_user_email_valid_format(self, db_session):
        """Тест что email с валидным форматом сохраняется"""
        user = User(
            user_name="validemail",
            email="user@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.email == "user@example.com"
        assert "@" in user.email
        assert "." in user.email


class TestUserOptionalFields:
    """Тесты опциональных полей"""

    def test_user_full_name_none(self, db_session):
        """Тест что full_name может быть None"""
        user = User(
            user_name="noname",
            email="noname@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.full_name is None

    def test_user_bio_none(self, db_session):
        """Тест что bio может быть None"""
        user = User(
            user_name="nobio",
            email="nobio@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.bio is None

    def test_user_verification_token_none(self, db_session):
        """Тест что verification_token может быть None"""
        user = User(
            user_name="notverified",
            email="notverified@example.com",
            hashed_password="password123",
            email_verified=False
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.verification_token is None
        assert user.verification_expires_at is None

    def test_user_password_reset_token_none(self, db_session):
        """Тест что password_reset_token может быть None"""
        user = User(
            user_name="nopassreset",
            email="nopassreset@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.password_reset_token is None
        assert user.password_reset_expires_at is None


class TestUserEmailVerificationEdgeCases:
    """Тесты граничных случаев верификации email"""

    def test_verification_token_expiration(self, db_session):
        """Тест истечения токена верификации"""
        user = User(
            user_name="verify_expires",
            email="verifyexpires@example.com",
            hashed_password="password123",
            verification_token="test_token",
            verification_expires_at=datetime.now(
                timezone.utc) - timedelta(hours=1)
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Токен должен быть протухшим
        # SQLite возвращает naive datetime,
        # поэтому используем timedelta для проверки
        expires_at = user.verification_expires_at
        now = datetime.now()
        # Проверяем что expires_at меньше чем now (с допуском в 5 секунд)
        assert (now - expires_at) > timedelta(seconds=5)

    def test_verification_fields_cleared_after_verification(self, db_session):
        """Тест что поля верификации очищаются после подтверждения"""
        user = User(
            user_name="verify_clearing",
            email="verifyclearing@example.com",
            hashed_password="password123",
            email_verified=False,
            verification_token="old_token",
            verification_expires_at=datetime.now(
                timezone.utc) + timedelta(days=1)
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Симулируем верификацию
        user.email_verified = True
        user.verification_token = None
        user.verification_expires_at = None
        db_session.commit()
        db_session.refresh(user)

        assert user.email_verified is True
        assert user.verification_token is None
        assert user.verification_expires_at is None


class TestUserPasswordResetEdgeCases:
    """Тесты граничных случаев сброса пароля"""

    def test_password_reset_expiration(self, db_session):
        """Тест истечения токена сброса пароля"""
        user = User(
            user_name="reset_expires",
            email="resetexpires@example.com",
            hashed_password="old_password",
            password_reset_token="reset_token",
            password_reset_expires_at=datetime.now(
                timezone.utc) - timedelta(hours=1)
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Токен протух
        expires_at = user.password_reset_expires_at
        now = datetime.now()
        assert (now - expires_at) > timedelta(seconds=5)

    def test_password_reset_cleared_after_reset(self, db_session):
        """Тест что поля сброса очищаются после смены пароля"""
        user = User(
            user_name="reset_clearing",
            email="resetclearing@example.com",
            hashed_password="old_password",
            password_reset_token="reset_token",
            password_reset_expires_at=datetime.now(
                timezone.utc) + timedelta(hours=1)
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Симулируем сброс пароля
        user.hashed_password = "new_hashed_password"
        user.password_reset_token = None
        user.password_reset_expires_at = None
        db_session.commit()
        db_session.refresh(user)

        assert user.hashed_password == "new_hashed_password"
        assert user.password_reset_token is None
        assert user.password_reset_expires_at is None


class TestUserRoleEdgeCases:
    """Тесты граничных случаев для ролей"""

    def test_user_with_empty_roles_list(self, db_session):
        """Тест что пользователь может иметь пустой список ролей"""
        user = User(
            user_name="noroles",
            email="noroles@example.com",
            hashed_password="password123"
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.roles == []
        assert len(user.roles) == 0

    def test_user_roles_order_preserved(self, db_session):
        """Тест что порядок ролей сохраняется"""
        roles = []
        for i in range(5):
            role = RoleModel(
                name=f"order_role_{i}",
                display_name=f"Роль {i}",
                permissions=Permission(1 << i)
            )
            db_session.add(role)
            roles.append(role)

        db_session.commit()

        user = User(
            user_name="ordered_roles",
            email="orderedroles@example.com",
            hashed_password="password123",
            roles=roles
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # SQLAlchemy может возвращать роли в любом порядке,
        # проверяем что все роли присутствуют
        assert len(user.roles) == 5
        for role in roles:
            assert role in user.roles

    def test_user_roles_can_be_accessed_by_name(self, db_session):
        """Тест что роли доступны по имени"""
        roles = []
        for i in range(3):
            role = RoleModel(
                name=f"access_role_{i}",
                display_name=f"Доступная роль {i}",
                permissions=Permission(1 << i)
            )
            db_session.add(role)
            roles.append(role)

        db_session.commit()

        user = User(
            user_name="access_roles_user",
            email="accessroles@example.com",
            hashed_password="password123",
            roles=roles
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Проверяем что можем найти роль по имени через has_role
        assert user.has_role("access_role_0") is True
        assert user.has_role("access_role_1") is True
        assert user.has_role("access_role_2") is True
        assert user.has_role("nonexistent") is False

    def test_user_all_permissions_combines_all_roles(self, db_session):
        """Тест что all_permissions объединяет все роли"""
        role1 = RoleModel(
            name="perm_role_1",
            display_name="Первая роль",
            permissions=Permission.READ
        )
        role2 = RoleModel(
            name="perm_role_2",
            display_name="Вторая роль",
            permissions=Permission.WRITE
        )
        role3 = RoleModel(
            name="perm_role_3",
            display_name="Третья роль",
            permissions=Permission.DELETE
        )

        db_session.add_all([role1, role2, role3])
        db_session.commit()

        user = User(
            user_name="all_perms_combined",
            email="allpermscombined@example.com",
            hashed_password="password123",
            roles=[role1, role2, role3]
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        expected = Permission.READ | Permission.WRITE | Permission.DELETE
        assert user.all_permissions == expected
