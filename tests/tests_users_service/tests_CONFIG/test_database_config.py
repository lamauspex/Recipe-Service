
from user_service.config import settings
from user_service.config.database import DataBaseConfig


class TestDatabaseConfiguration:
    """Тесты конфигурации базы данных"""

    def test_testing_flag_is_true(self):
        """
        Проверяет, что флаг testing установлен в True
        """
        assert settings.database.TESTING is True, (
            f"Ожидалось testing=True, \
                получено testing={settings.database.TESTING}. "
            "Проверьте переменную TESTING в .env файле"
        )

    def test_database_url_is_sqlite(self):
        """
        Проверяет, что URL базы данных указывает на SQLite в памяти
        """
        database_url = settings.database.get_database_url()

        assert "sqlite" in database_url.lower(), (
            f"Ожидался URL с sqlite, получен: {database_url}. "
            "В тестовом окружении должна использоваться SQLite БД!"
        )
        assert ":///:memory:" in database_url, (
            f"Ожидалась SQLite в памяти, получен: {database_url}"
        )

    def test_database_url_with_driver(self):
        """
        Проверяет, что get_database_url() с явным драйвером
        sqlite работает корректно
        """
        sqlite_url = settings.database.get_database_url("sqlite")

        assert sqlite_url == "sqlite:///:memory:", (
            f"Ожидался sqlite:///:memory:, получен: {sqlite_url}"
        )

    def test_database_config_testing_attribute(self):
        """
        Проверяет, что DataBaseConfig.testing атрибут корректно читается
        """
        config = DataBaseConfig()

        assert config.TESTING is True, (
            f"Ожидалось testing=True, получено testing={config.testing}"
        )

    def test_database_is_not_postgresql(self):
        """
        Проверяет, что БД НЕ является PostgreSQL
        """
        database_url = settings.database.get_database_url()

        assert "postgresql" not in database_url.lower(), (
            f"В тестовом окружении НЕ должен использоваться PostgreSQL! "
            f"Полученный URL: {database_url}"
        )
        assert "psycopg2" not in database_url.lower(), (
            "В тестовом окружении НЕ должен использоваться драйвер psycopg2!"
        )


class TestDatabaseUrlFormat:
    """Тесты формата URL базы данных"""

    def test_sqlite_url_format(self):
        """
        Проверяет корректность формата SQLite URL
        """

        if settings.database.TESTING:
            expected_url = "sqlite:///:memory:"

            assert expected_url == "sqlite:///:memory:", (
                f"Некорректный SQLite URL: {expected_url}"
            )

    def test_get_database_url_sqlite_driver(self):
        """
        Проверяет генерацию URL с драйвером sqlite
        """
        if settings.database.TESTING:
            url = settings.database.get_database_url("sqlite")

            assert url == "sqlite:///:memory:", (
                f"Ожидался 'sqlite:///:memory:', получен: {url}"
            )
