""" Tests Settings"""

from user_service.config.auth import AuthConfig
from user_service.config.cache import CacheConfig
from user_service.config.database import DataBaseConfig
from user_service.config.monitoring import MonitoringConfig
from user_service.config.settings import Settings, settings
from user_service.config.api import ApiConfig


class TestSettings:
    """ Тесты для центрального объекта конфигурации Settings """

    def test_settings_has_nested_configs(self):
        """
        Test that Settings contains all nested configs
        """

        assert hasattr(Settings(), 'api')
        assert hasattr(Settings(), 'auth')
        assert hasattr(Settings(), 'database')
        assert hasattr(Settings(), 'cache')
        assert hasattr(Settings(), 'monitoring')

    def test_settings_api_access(self):
        """
        Test accessing API config through Settings
        """

        settings = Settings()

        # API config fields are accessed via settings.api
        assert hasattr(settings.api, 'HOST')
        assert hasattr(settings.api, 'PORT')
        assert hasattr(settings.api, 'ENVIRONMENT')
        assert hasattr(settings.api, 'API_DOCS_ENABLED')
        assert hasattr(settings.api, 'API_TITLE')
        assert hasattr(settings.api, 'API_VERSION')

    def test_settings_api_config_is_apiconfig(self):
        """
        Test that settings.api is instance of ApiConfig
        """

        settings = Settings()
        assert isinstance(settings.api, ApiConfig)

    def test_settings_has_all_required_attributes(self):
        """
        Тест: Settings содержит все обязательные атрибуты
        """

        required_attrs = [
            'auth',
            'database',
            'api',
            'cache',
            'monitoring'
        ]

        for attr in required_attrs:
            assert hasattr(
                settings,
                attr
            ), f"Settings должен содержать атрибут '{attr}'"

    def test_settings_attributes_are_not_none(self):
        """
        Тест: Все атрибуты Settings инициализированы
        """

        assert settings.auth is not None
        assert settings.database is not None
        assert settings.api is not None
        assert settings.cache is not None
        assert settings.monitoring is not None

    def test_settings_auth_is_auth_config_instance(self):
        """
        Тест: settings.auth является экземпляром AuthConfig
        """

        assert isinstance(settings.auth, AuthConfig)

    def test_settings_api_is_api_config_instance(self):
        """
        Тест: settings.api является экземпляром ApiConfig
        """

        assert isinstance(settings.api, ApiConfig)

    def test_settings_database_is_database_config_instance(self):
        """
        Тест: settings.database является экземпляром DatabaseConfig
        """

        assert isinstance(settings.database, DataBaseConfig)

    def test_settings_cache_is_cache_config_instance(self):
        """
        Тест: settings.cache является экземпляром CacheConfig
        """

        assert isinstance(settings.cache, CacheConfig)

    def test_settings_monitoring_is_monitoring_config_instance(self):
        """
        Тест: settings.monitoring является экземпляром MonitoringConfig
        """

        assert isinstance(settings.monitoring, MonitoringConfig)

    def test_settings_nested_access_api_config(self):
        """
        Тест: Доступ к вложенным полям через settings.api
        """

        # Проверяем, что можем обратиться к полям api_config
        assert hasattr(settings.api, 'HOST')
        assert hasattr(settings.api, 'PORT')
        assert hasattr(settings.api, 'API_TITLE')

    def test_settings_nested_access_auth_config(self):
        """
        Тест: Доступ к вложенным полям через settings.auth
        """

        # Проверяем, что можем обратиться к полям auth_config
        assert hasattr(settings.auth, 'SECRET_KEY')
        assert hasattr(settings.auth, 'ALGORITHM')

    def test_settings_is_singleton(self):
        """
        Тест: Settings — синглтон
        """

        # Один и тот же объект
        settings_1 = Settings()
        settings_2 = Settings()

        assert settings_1 is settings_2
