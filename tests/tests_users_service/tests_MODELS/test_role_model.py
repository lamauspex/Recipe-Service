"""
Тесты для модели RoleModel и системы разрешений
"""

import pytest

from user_service.models.role_model import (
    RoleModel,
    Permission,
    DEFAULT_ROLES
)
from user_service.models.user_models import User


class TestPermission:
    """Тесты для системы разрешений Permission"""

    def test_permission_none(self):
        """Тест Permission.NONE"""
        assert Permission.NONE == 0

    def test_permission_read(self):
        """Тест Permission.READ"""
        assert Permission.READ == 1
        assert bool(Permission.READ) is True

    def test_permission_write(self):
        """Тест Permission.WRITE"""
        assert Permission.WRITE == 2

    def test_permission_delete(self):
        """Тест Permission.DELETE"""
        assert Permission.DELETE == 4

    def test_permission_manage_users(self):
        """Тест Permission.MANAGE_USERS"""
        assert Permission.MANAGE_USERS == 8

    def test_permission_manage_roles(self):
        """Тест Permission.MANAGE_ROLES"""
        assert Permission.MANAGE_ROLES == 16

    def test_permission_view_stats(self):
        """Тест Permission.VIEW_STATS"""
        assert Permission.VIEW_STATS == 32

    def test_permission_system_config(self):
        """Тест Permission.SYSTEM_CONFIG"""
        assert Permission.SYSTEM_CONFIG == 64

    def test_permission_ban_users(self):
        """Тест Permission.BAN_USERS"""
        assert Permission.BAN_USERS == 128

    def test_permission_full_access(self):
        """Тест Permission.FULL_ACCESS"""
        assert Permission.FULL_ACCESS == 255

    def test_permission_bitwise_or(self):
        """Тест объединения разрешений через OR"""
        combined = Permission.READ | Permission.WRITE
        assert combined == 3  # 1 | 2 = 3

    def test_permission_bitwise_and(self):
        """Тест проверки разрешения через AND"""
        full = Permission.FULL_ACCESS
        assert bool(full & Permission.READ) is True
        assert bool(full & Permission.WRITE) is True
        assert bool(full & Permission.DELETE) is True

    def test_permission_not_present(self):
        """Тест отсутствия разрешения"""
        read_only = Permission.READ
        assert bool(read_only & Permission.WRITE) is False

    def test_permission_intflag_behavior(self):
        """Тест поведения IntFlag"""
        # Проверяем, что Permission можно использовать как int
        assert isinstance(Permission.READ, int)
        assert int(Permission.READ) == 1

        # Проверяем сложение разрешений
        result = Permission.READ + Permission.WRITE
        assert result == 3

    def test_permission_enumerate(self):
        """Тест перечисления разрешений"""
        # Получаем только простые (atomic) флаги, не NONE и не комбинации
        simple_permissions = [
            Permission.READ,
            Permission.WRITE,
            Permission.DELETE,
            Permission.MANAGE_USERS,
            Permission.MANAGE_ROLES,
            Permission.VIEW_STATS,
            Permission.SYSTEM_CONFIG,
            Permission.BAN_USERS
        ]
        # Проверяем что все простые флаги присутствуют в перечислении
        for perm in simple_permissions:
            assert perm in list(Permission)

    def test_permission_full_access_is_combination(self):
        """Тест что FULL_ACCESS это комбинация всех флагов"""
        all_simple = (
            Permission.READ | Permission.WRITE | Permission.DELETE |
            Permission.MANAGE_USERS | Permission.MANAGE_ROLES |
            Permission.VIEW_STATS | Permission.SYSTEM_CONFIG | Permission.BAN_USERS
        )
        assert Permission.FULL_ACCESS == all_simple
        assert Permission.FULL_ACCESS == 255


class TestRoleModel:
    """Тесты для модели RoleModel"""

    def test_role_model_creation(self, db_session):
        """Тест создания роли"""

        role = RoleModel(
            name="test_role",
            display_name="Тестовая роль",
            description="Роль для тестирования",
            permissions=Permission.READ | Permission.WRITE,
            is_system=False,
            is_active=True
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert role.id is not None
        assert role.name == "test_role"
        assert role.display_name == "Тестовая роль"
        assert role.description == "Роль для тестирования"
        assert role.permissions == 3  # READ | WRITE = 3
        assert role.is_system is False
        assert role.is_active is True

    def test_role_model_repr(self, db_session):
        """Тест строкового представления роли"""

        role = RoleModel(
            name="repr_role",
            display_name="Роль для repr",
            permissions=Permission.READ
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        repr_str = repr(role)
        assert "Role" in repr_str
        assert "repr_role" in repr_str
        assert "permissions=1" in repr_str

    def test_role_default_permissions(self, db_session):
        """Тест дефолтных разрешений"""

        role = RoleModel(
            name="default_perms",
            display_name="Роль с дефолтными правами"
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        # По умолчанию Permission.NONE = 0
        assert role.permissions == Permission.NONE

    def test_role_default_is_system(self, db_session):
        """Тест дефолтного значения is_system"""

        role = RoleModel(
            name="default_system",
            display_name="Не системная роль"
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert role.is_system is False

    def test_role_default_is_active(self, db_session):
        """Тест дефолтного значения is_active"""

        role = RoleModel(
            name="default_active",
            display_name="Активная роль"
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert role.is_active is True

    def test_role_has_permission_method(self, db_session):
        """Тест метода has_permission"""

        role = RoleModel(
            name="perm_test",
            display_name="Тест разрешений",
            permissions=Permission.READ | Permission.WRITE
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert role.has_permission(Permission.READ) is True
        assert role.has_permission(Permission.WRITE) is True
        assert role.has_permission(Permission.DELETE) is False

    def test_role_add_permission(self, db_session):
        """Тест добавления разрешения"""

        role = RoleModel(
            name="add_perm",
            display_name="Добавление разрешения",
            permissions=Permission.READ
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert role.permissions == Permission.READ

        # Добавляем разрешение
        role.add_permission(Permission.WRITE)
        db_session.commit()
        db_session.refresh(role)

        assert role.has_permission(Permission.WRITE) is True
        assert role.permissions == (Permission.READ | Permission.WRITE)

    def test_role_remove_permission(self, db_session):
        """Тест удаления разрешения"""

        role = RoleModel(
            name="remove_perm",
            display_name="Удаление разрешения",
            permissions=Permission.READ | Permission.WRITE | Permission.DELETE
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        assert role.permissions == 7  # 1 | 2 | 4 = 7

        # Удаляем разрешение DELETE
        role.remove_permission(Permission.DELETE)
        db_session.commit()
        db_session.refresh(role)

        assert role.has_permission(Permission.DELETE) is False
        assert role.has_permission(Permission.READ) is True
        assert role.has_permission(Permission.WRITE) is True

    def test_role_permissions_list_property(self, db_session):
        """Тест свойства permissions_list"""

        role = RoleModel(
            name="perms_list",
            display_name="Список разрешений",
            permissions=Permission.READ | Permission.WRITE | Permission.DELETE
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        perms_list = role.permissions_list

        assert isinstance(perms_list, list)
        assert Permission.READ in perms_list
        assert Permission.WRITE in perms_list
        assert Permission.DELETE in perms_list
        assert Permission.NONE not in perms_list

    def test_role_permissions_list_empty(self, db_session):
        """Тест пустого списка разрешений"""

        role = RoleModel(
            name="no_perms",
            display_name="Без разрешений",
            permissions=Permission.NONE
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        perms_list = role.permissions_list
        assert len(perms_list) == 0

    def test_role_unique_name_constraint(self, db_session):
        """Тест уникальности имени роли"""

        role1 = RoleModel(
            name="unique_role",
            display_name="Первая роль"
        )
        db_session.add(role1)
        db_session.commit()

        role2 = RoleModel(
            name="unique_role",  # Дубликат
            display_name="Вторая роль"
        )
        db_session.add(role2)

        with pytest.raises(Exception):
            db_session.commit()

        db_session.rollback()

    def test_role_multiple_permissions(self, db_session):
        """Тест нескольких разрешений"""

        role = RoleModel(
            name="multi_perms",
            display_name="Много разрешений",
            permissions=Permission.READ | Permission.WRITE |
            Permission.DELETE | Permission.VIEW_STATS
        )

        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)

        expected = Permission.READ | Permission.WRITE | Permission.DELETE | Permission.VIEW_STATS
        assert role.permissions == expected


class TestUserRolesRelationship:
    """Тесты связи User и RoleModel"""

    def test_user_roles_relationship(self, db_session):
        """Тест связи пользователя с ролями"""

        # Создаем роли
        user_role = RoleModel(
            name="test_user_role",
            display_name="Тестовая роль",
            permissions=Permission.READ
        )
        admin_role = RoleModel(
            name="test_admin_role",
            display_name="Тестовый админ",
            permissions=Permission.FULL_ACCESS
        )

        db_session.add_all([user_role, admin_role])
        db_session.commit()

        # Создаем пользователя с ролями
        user = User(
            user_name="multi_role_user",
            email="multirole@example.com",
            hashed_password="password123",
            roles=[user_role, admin_role]
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.roles) == 2
        assert user_role in user.roles
        assert admin_role in user.roles

    def test_user_add_role_method(self, db_session):
        """Тест метода add_role"""

        user = User(
            user_name="add_role_user",
            email="addrole@example.com",
            hashed_password="password123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        role = RoleModel(
            name="addable_role",
            display_name="Добавляемая роль",
            permissions=Permission.READ
        )
        db_session.add(role)
        db_session.commit()

        assert len(user.roles) == 0

        # Добавляем роль
        user.add_role(role)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.roles) == 1
        assert role in user.roles

    def test_user_add_role_duplicate(self, db_session):
        """Тест добавления дублирующей роли"""

        role = RoleModel(
            name="duplicate_role",
            display_name="Роль для дублирования",
            permissions=Permission.READ
        )
        db_session.add(role)
        db_session.commit()

        user = User(
            user_name="dup_role_user",
            email="duprole@example.com",
            hashed_password="password123",
            roles=[role]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.roles) == 1

        # Пытаемся добавить ту же роль again
        user.add_role(role)
        db_session.commit()
        db_session.refresh(user)

        # Роль должна остаться только одна
        assert len(user.roles) == 1

    def test_user_remove_role_method(self, db_session):
        """Тест метода remove_role"""

        role = RoleModel(
            name="removable_role",
            display_name="Удаляемая роль",
            permissions=Permission.READ
        )
        db_session.add(role)
        db_session.commit()

        user = User(
            user_name="remove_role_user",
            email="removerole@example.com",
            hashed_password="password123",
            roles=[role]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.roles) == 1

        # Удаляем роль
        user.remove_role(role)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.roles) == 0

    def test_user_remove_nonexistent_role(self, db_session):
        """Тест удаления несуществующей роли"""

        role = RoleModel(
            name="other_role",
            display_name="Другая роль",
            permissions=Permission.READ
        )
        db_session.add(role)
        db_session.commit()

        user = User(
            user_name="no_role_user",
            email="norole@example.com",
            hashed_password="password123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Пытаемся удалить роль, которой нет
        user.remove_role(role)
        db_session.commit()

        assert len(user.roles) == 0  # Должно остаться пустым

    def test_user_has_role_method(self, db_session):
        """Тест метода has_role"""

        role1 = RoleModel(
            name="has_role_1",
            display_name="Первая роль",
            permissions=Permission.READ
        )
        role2 = RoleModel(
            name="has_role_2",
            display_name="Вторая роль",
            permissions=Permission.WRITE
        )

        db_session.add_all([role1, role2])
        db_session.commit()

        user = User(
            user_name="has_role_user",
            email="hasrole@example.com",
            hashed_password="password123",
            roles=[role1]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.has_role("has_role_1") is True
        assert user.has_role("has_role_2") is False
        assert user.has_role("nonexistent") is False

    def test_user_primary_role_property(self, db_session):
        """Тест свойства primary_role"""

        role1 = RoleModel(
            name="primary_role_1",
            display_name="Первая роль",
            permissions=Permission.READ
        )
        role2 = RoleModel(
            name="primary_role_2",
            display_name="Вторая роль",
            permissions=Permission.WRITE
        )

        db_session.add_all([role1, role2])
        db_session.commit()

        user = User(
            user_name="primary_role_user",
            email="primaryrole@example.com",
            hashed_password="password123",
            roles=[role1, role2]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # primary_role должен возвращать первую роль
        assert user.primary_role == role1

    def test_user_primary_role_empty(self, db_session):
        """Тест primary_role когда ролей нет"""

        user = User(
            user_name="no_primary_user",
            email="noprimary@example.com",
            hashed_password="password123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.primary_role is None

    def test_user_all_permissions_property(self, db_session):
        """Тест свойства all_permissions"""

        role1 = RoleModel(
            name="all_perms_1",
            display_name="Первая роль",
            permissions=Permission.READ
        )
        role2 = RoleModel(
            name="all_perms_2",
            display_name="Вторая роль",
            permissions=Permission.WRITE
        )

        db_session.add_all([role1, role2])
        db_session.commit()

        user = User(
            user_name="all_perms_user",
            email="allperms@example.com",
            hashed_password="password123",
            roles=[role1, role2]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # all_permissions должен объединять разрешения всех ролей
        expected = Permission.READ | Permission.WRITE
        assert user.all_permissions == expected

    def test_user_all_permissions_no_roles(self, db_session):
        """Тест all_permissions когда ролей нет"""

        user = User(
            user_name="no_all_perms_user",
            email="noallperms@example.com",
            hashed_password="password123"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.all_permissions == Permission.NONE

    def test_user_has_permission_method(self, db_session):
        """Тест метода has_permission у пользователя"""

        role = RoleModel(
            name="user_perm_test",
            display_name="Тест разрешений",
            permissions=Permission.READ | Permission.WRITE
        )
        db_session.add(role)
        db_session.commit()

        user = User(
            user_name="has_perm_user",
            email="hasperm@example.com",
            hashed_password="password123",
            roles=[role]
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.has_permission(Permission.READ) is True
        assert user.has_permission(Permission.WRITE) is True
        assert user.has_permission(Permission.DELETE) is False


class TestDefaultRoles:
    """Тесты констант DEFAULT_ROLES"""

    def test_default_roles_exist(self):
        """Тест наличия дефолтных ролей"""

        assert "user" in DEFAULT_ROLES
        assert "moderator" in DEFAULT_ROLES
        assert "admin" in DEFAULT_ROLES

    def test_default_user_role(self):
        """Тест структуры роли user"""

        user_role = DEFAULT_ROLES["user"]
        assert user_role["display_name"] == "Пользователь"
        assert user_role["description"] == "Базовые права доступа"
        assert user_role["permissions"] == Permission.READ
        assert user_role["is_system"] is True

    def test_default_moderator_role(self):
        """Тест структуры роли moderator"""

        mod_role = DEFAULT_ROLES["moderator"]
        assert mod_role["display_name"] == "Модератор"
        assert mod_role["description"] == "Права на модерацию контента"
        assert mod_role["permissions"] == (Permission.READ |
                                           Permission.WRITE |
                                           Permission.VIEW_STATS)
        assert mod_role["is_system"] is True

    def test_default_admin_role(self):
        """Тест структуры роли admin"""

        admin_role = DEFAULT_ROLES["admin"]
        assert admin_role["display_name"] == "Администратор"
        assert admin_role["description"] == "Полный доступ к системе"
        assert admin_role["permissions"] == Permission.FULL_ACCESS
        assert admin_role["is_system"] is True


class TestUserRolesConstraints:
    """Тесты ограничений связей User-Role"""

    def test_role_users_relationship(self, db_session):
        """Тест связи role.users"""

        role = RoleModel(
            name="role_users_test",
            display_name="Тест связи users",
            permissions=Permission.READ
        )
        db_session.add(role)
        db_session.commit()

        # Создаем пользователей с этой ролью
        users = []
        for i in range(3):
            user = User(
                user_name=f"role_user_{i}",
                email=f"roleuser{i}@example.com",
                hashed_password="password123",
                roles=[role]
            )
            db_session.add(user)
            users.append(user)

        db_session.commit()
        db_session.refresh(role)

        # Проверяем связь в обратную сторону
        assert len(role.users) == 3
        for user in users:
            assert user in role.users

    def test_multiple_users_same_role(self, db_session):
        """Тест нескольких пользователей с одной ролью"""

        role = RoleModel(
            name="shared_role",
            display_name="Общая роль",
            permissions=Permission.READ
        )
        db_session.add(role)
        db_session.commit()

        user1 = User(
            user_name="shared_user_1",
            email="shareduser1@example.com",
            hashed_password="password123",
            roles=[role]
        )
        user2 = User(
            user_name="shared_user_2",
            email="shareduser2@example.com",
            hashed_password="password123",
            roles=[role]
        )

        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(role)

        assert len(role.users) == 2
        assert user1 in role.users
        assert user2 in role.users

    def test_user_with_multiple_roles(self, db_session):
        """Тест пользователя с несколькими ролями"""

        roles = []
        for i in range(3):
            role = RoleModel(
                name=f"multi_role_{i}",
                display_name=f"Роль {i}",
                permissions=Permission(1 << i)  # READ, WRITE, DELETE
            )
            db_session.add(role)
            roles.append(role)

        db_session.commit()

        user = User(
            user_name="multi_roles_user",
            email="multiroles@example.com",
            hashed_password="password123",
            roles=roles
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert len(user.roles) == 3
        for role in roles:
            assert role in user.roles
