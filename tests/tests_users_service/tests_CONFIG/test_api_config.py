"""
Тесты для конфигурации API (user_service/config/api.py)
"""

import os
from unittest.mock import patch

from user_service.config.api import ApiConfig


class TestApiConfig:
    """Тесты для ApiConfig"""

    def test_api_config_defaults(self):
        """Тест создания ApiConfig с явными значениями"""

        config = ApiConfig(
            HOST="127.0.0.1",
            PORT=8000,
            ENVIRONMENT='development',
            API_DOCS_ENABLED=True,
            API_DESCRIPTION='API для управления',
            API_TITLE="Test API",
            API_VERSION="1.0.0"
        )

        assert config.HOST == "127.0.0.1"
        assert config.PORT == 8000
        assert config.ENVIRONMENT == 'development'
        assert config.API_DESCRIPTION == 'API для управления'
        assert config.API_DOCS_ENABLED is True
        assert config.API_TITLE == "Test API"
        assert config.API_VERSION == "1.0.0"

    def test_api_config_types(self):
        """Тест типов полей ApiConfig"""

        config = ApiConfig(
            HOST="0.0.0.0",
            PORT=8080,
            ENVIRONMENT="production",
            API_DOCS_ENABLED=False,
            API_TITLE="Production API",
            API_DESCRIPTION="Ready for production!",
            API_VERSION="2.0.0"
        )

        assert isinstance(config.HOST, str)
        assert isinstance(config.PORT, int)
        assert isinstance(config.ENVIRONMENT, str)
        assert isinstance(config.API_DESCRIPTION, str)
        assert isinstance(config.API_DOCS_ENABLED, bool)
        assert isinstance(config.API_TITLE, str)
        assert isinstance(config.API_VERSION, str)

    def test_api_config_validation_host(self):
        """Тест валидации поля HOST"""

        # HOST должен быть строкой
        config = ApiConfig(
            HOST="192.168.1.1",
            PORT=8000,
            DEBUG=True,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=True,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        assert config.HOST == "192.168.1.1"

    def test_api_config_validation_port(self):
        """Тест валидации поля PORT"""

        # PORT должен быть положительным int
        config = ApiConfig(
            HOST="localhost",
            PORT=1,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        assert config.PORT == 1

    def test_api_config_validation_port_negative(self):
        """
        Тест что отрицательный порт принимается
        (Pydantic не ограничивает int)
        """

        # Pydantic принимает отрицательные int без ошибки валидации
        config = ApiConfig(
            HOST="localhost",
            PORT=-1,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )
        assert config.PORT == -1

    def test_api_config_validation_port_zero(self):
        """Тест что порт 0 может быть принят (системный порт)"""

        config = ApiConfig(
            HOST="0.0.0.0",
            PORT=0,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        assert config.PORT == 0

    def test_api_config_api_docs_enabled(self):
        """Тест поля API_DOCS_ENABLED"""

        config_enabled = ApiConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=True,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        config_disabled = ApiConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=False,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        assert config_enabled.API_DOCS_ENABLED is True
        assert config_disabled.API_DOCS_ENABLED is False

    def test_api_config_version_format(self):
        """Тест формата версии API"""

        config = ApiConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0.0"
        )

        assert config.API_VERSION == "1.0.0"

    def test_api_config_title(self):
        """Тест заголовка API"""

        config = ApiConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="User Management API",
            API_VERSION="1.0.0"
        )

        assert config.API_TITLE == "User Management API"


class TestApiConfigEnvVariables:
    """Тесты загрузки ApiConfig из env переменных"""

    def test_api_config_env_host(self):
        """Тест что env переменные влияют на конфигурацию"""

        # Создаем тестовый класс с явными значениями
        class TestApiConfig(ApiConfig):
            pass

        with patch.dict(os.environ, {
            "USER_SERVICE_HOST": "10.0.0.1",
            "USER_SERVICE_PORT": "9000",
            "USER_SERVICE_ENVIRONMENT": "development",

            "USER_SERVICE_API_DOCS_ENABLED": "true",
            "USER_SERVICE_API_DESCRIPTION": "API for you",
            "USER_SERVICE_API_TITLE": "Env API",
            "USER_SERVICE_API_VERSION": "2.0.0",

        }):
            config = TestApiConfig()

            assert config.HOST == "10.0.0.1"
            assert config.PORT == 9000
            assert config.API_DOCS_ENABLED is True

    def test_api_config_env_port_type_conversion(self):
        """Тест автоматического преобразования типов из env"""

        class TestApiConfig(ApiConfig):
            pass

        with patch.dict(os.environ, {
            "USER_SERVICE_HOST": "192.168.1.100",
            "USER_SERVICE_PORT": "8080",
            "USER_SERVICE_ENVIRONMENT": "http://test.com",
            "USER_SERVICE_API_DESCRIPTION": "false",
            "USER_SERVICE_API_DOCS_ENABLED": "false",
            "USER_SERVICE_API_TITLE": "Test",
            "USER_SERVICE_API_VERSION": "1.0"
        }):
            config = TestApiConfig()

            # PORT должен быть int, а не str
            assert isinstance(config.PORT, int)
            assert config.PORT == 8080


class TestApiConfigAssignment:
    """
    Тесты присваивания значений после создания
    (validate_assignment=True)
    """

    def test_api_config_update_host(self):
        """Тест обновления HOST"""

        config = ApiConfig(
            HOST="127.0.0.1",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        config.HOST = "0.0.0.0"
        assert config.HOST == "0.0.0.0"

    def test_api_config_update_port(self):
        """Тест обновления PORT"""

        config = ApiConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        config.PORT = 8080
        assert config.PORT == 8080

    def test_api_config_port_type_conversion(self):
        """Тест что PORT автоматически конвертирует строки в int"""

        config = ApiConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        # Pydantic v2 автоматически конвертирует строки в int
        config.PORT = "8080"
        assert config.PORT == 8080
        assert isinstance(config.PORT, int)


class TestApiConfigSingleton:
    """Тесты для api_config singleton"""

    def test_api_config_is_instance(self):
        """Тест что api_config создается как экземпляр ApiConfig"""

        from user_service.config.api import api_config

        assert api_config is not None
        assert isinstance(api_config, ApiConfig)

    def test_api_config_has_required_fields(self):
        """Тест что api_config имеет все обязательные поля"""

        from user_service.config.api import api_config

        assert hasattr(api_config, 'HOST')
        assert hasattr(api_config, 'PORT')
        assert hasattr(api_config, 'ENVIRONMENT')
        assert hasattr(api_config, 'API_DESCRIPTION')
        assert hasattr(api_config, 'API_DOCS_ENABLED')
        assert hasattr(api_config, 'API_TITLE')
        assert hasattr(api_config, 'API_VERSION')

    def test_api_config_fields_types(self):
        """Тест что api_config имеет корректные типы полей"""

        from user_service.config.api import api_config

        assert isinstance(api_config.HOST, str)
        assert isinstance(api_config.PORT, int)
        assert isinstance(api_config.ENVIRONMENT, str)
        assert isinstance(api_config.API_DOCS_ENABLED, bool)
        assert isinstance(api_config.API_DESCRIPTION, str)
        assert isinstance(api_config.API_TITLE, str)
        assert isinstance(api_config.API_VERSION, str)


class TestApiConfigTesting:
    """Тесты для production сценариев"""

    def test_api_config_testing_settings(self):
        """Тест testing настроек"""

        config = ApiConfig(
            HOST="127.0.0.1",
            PORT=8001,
            DEBUG=True,
            CORS_ORIGINS=["http://test.com"],
            CORS_ALLOW_CREDENTIALS=True,
            API_DOCS_ENABLED=True,
            API_TITLE="Test API",
            API_VERSION="test"
        )

        assert config.PORT == 8001  # Отличаемся от стандартного
        assert config.API_VERSION == "test"


class TestApiConfigEquality:
    """Тесты сравнения конфигураций"""

    def test_api_config_equality(self):
        """Тест равенства конфигураций"""

        config_1 = ApiConfig(
            HOST="localhost",
            PORT=8000,
            ENVIRONMENT="production",

            API_DOCS_ENABLED=True,
            API_DESCRIPTION="Просто проверка",
            API_TITLE="API",
            API_VERSION="1.0"
        )

        config_2 = ApiConfig(
            HOST="localhost",
            PORT=8000,
            ENVIRONMENT="production",

            API_DOCS_ENABLED=True,
            API_DESCRIPTION="Просто проверка",
            API_TITLE="API",
            API_VERSION="1.0"
        )

        assert config_1.HOST == config_2.HOST
        assert config_1.PORT == config_2.PORT
        assert config_1.ENVIRONMENT == config_2.ENVIRONMENT

        assert config_1.API_DOCS_ENABLED == config_2.API_DOCS_ENABLED
        assert config_1.API_DESCRIPTION == config_2.API_DESCRIPTION
        assert config_1.API_TITLE == config_2.API_TITLE
        assert config_1.API_VERSION == config_2.API_VERSION

    def test_api_config_inequality(self):
        """Тест неравенства конфигураций"""

        config1 = ApiConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=["http://example.com"],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        config2 = ApiConfig(
            HOST="0.0.0.0",  # Различие
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=["http://example.com"],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        assert config1.HOST != config2.HOST

    def test_api_config_dict_conversion(self):
        """Тест преобразования в словарь"""

        config = ApiConfig(
            HOST="localhost",
            PORT=8000,
            ENVIRONMENT="Среда",

            API_DOCS_ENABLED=True,
            API_DESCRIPTION="API",
            API_TITLE="API",
            API_VERSION="1.0"
        )

        config_dict = config.model_dump()

        assert isinstance(config_dict, dict)
        assert config_dict['HOST'] == "localhost"
        assert config_dict['PORT'] == 8000
        assert config_dict['API_DOCS_ENABLED'] is True
