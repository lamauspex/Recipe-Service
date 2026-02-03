""" Тесты для конфигурации Monitoring """


import os
from unittest.mock import patch
import pytest
from pydantic import ValidationError

from user_service.config.monitoring import MonitoringConfig


class TestMonitoringConfig:
    """
    Тесты для конфигураций ApiConfig
    """

    def test_api_config_cors_origins_list(self):
        """Тест что CORS_ORIGINS является списком"""

        config = MonitoringConfig(
            # ЛОГИРОВАНИЕ
            LOG_LEVEL="INFO",
            LOG_FORMAT="json",
            STRUCTURED_LOGGING=False,
            ENABLE_REQUEST_LOGGING=True,
            ENABLE_EXCEPTION_LOGGING=True,
            ENABLE_BUSINESS_LOGGING=True,
            # МОНИТОРИНГ
            MONITORING_ENABLED=False,
            METRICS_PORT="4000",
            HEALTH_CHECK_PATH="abc",
            PROMETHEUS_METRICS_PATH="abc",
            # CORS НАСТРОЙКИ
            CORS_ORIGINS=[
                "http://localhost:3000",
                "http://localhost:8080",
                "https://production.com"
            ],
            CORS_ALLOW_CREDENTIALS="true",
            CORS_MAX_AGE="900",
        )

        assert len(config.CORS_ORIGINS) == 3
        assert "http://localhost:3000" in config.CORS_ORIGINS
        assert "http://localhost:8080" in config.CORS_ORIGINS
        assert "https://production.com" in config.CORS_ORIGINS

    def test_api_config_empty_cors_origins(self):
        """Тест пустого списка CORS_ORIGINS"""

        config = MonitoringConfig(
            # ЛОГИРОВАНИЕ
            LOG_LEVEL="INFO",
            LOG_FORMAT="json",
            STRUCTURED_LOGGING=False,
            ENABLE_REQUEST_LOGGING=True,
            ENABLE_EXCEPTION_LOGGING=True,
            ENABLE_BUSINESS_LOGGING=True,
            # МОНИТОРИНГ
            MONITORING_ENABLED=False,
            METRICS_PORT="4000",
            HEALTH_CHECK_PATH="abc",
            PROMETHEUS_METRICS_PATH="abc",
            # CORS НАСТРОЙКИ
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS="true",
            CORS_MAX_AGE="900",
        )

        assert config.CORS_ORIGINS == []
        assert len(config.CORS_ORIGINS) == 0

    def test_api_config_validation_cors_credentials(self):
        """Тест поля CORS_ALLOW_CREDENTIALS"""

        config_true = MonitoringConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=["http://localhost:3000"],
            CORS_ALLOW_CREDENTIALS=True,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        config_false = MonitoringConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=["http://localhost:3000"],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        assert config_true.CORS_ALLOW_CREDENTIALS is True
        assert config_false.CORS_ALLOW_CREDENTIALS is False

    def test_api_config_update_cors_origins(self):
        """Тест обновления CORS_ORIGINS"""

        config = MonitoringConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        config.CORS_ORIGINS = ["http://new-origin.com"]
        assert config.CORS_ORIGINS == ["http://new-origin.com"]

    def test_api_config_cors_credentials_type_conversion(self):
        """Тест что CORS_ALLOW_CREDENTIALS конвертирует типы"""

        config = MonitoringConfig(
            HOST="localhost",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=[],
            CORS_ALLOW_CREDENTIALS=False,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        # Pydantic v2 автоматически конвертирует "true"/"yes" в True
        config.CORS_ALLOW_CREDENTIALS = "true"
        assert config.CORS_ALLOW_CREDENTIALS is True

        config.CORS_ALLOW_CREDENTIALS = "yes"
        assert config.CORS_ALLOW_CREDENTIALS is True

        # Число становится bool
        config.CORS_ALLOW_CREDENTIALS = 1
        assert config.CORS_ALLOW_CREDENTIALS is True

        config.CORS_ALLOW_CREDENTIALS = 0
        assert config.CORS_ALLOW_CREDENTIALS is False

        # Пустая строка вызывает ошибку валидации
        with pytest.raises(ValidationError):
            config.CORS_ALLOW_CREDENTIALS = ""

    def test_api_config_env_cors_json_parsing(self):
        """Тест парсинга CORS_ORIGINS из env (JSON формат)"""

        class TestApiConfig(MonitoringConfig):
            pass

        with patch.dict(os.environ, {
            "USER_SERVICE_HOST": "localhost",
            "USER_SERVICE_PORT": "8000",
            "USER_SERVICE_DEBUG": "false",
            "USER_SERVICE_CORS_ORIGINS": '["http://localhost:3000",\
                "https://example.com"]',
            "USER_SERVICE_CORS_ALLOW_CREDENTIALS": "true",
            "USER_SERVICE_API_DOCS_ENABLED": "true",
            "USER_SERVICE_API_TITLE": "API",
            "USER_SERVICE_API_VERSION": "1.0"
        }):
            config = TestApiConfig()

            assert isinstance(config.CORS_ORIGINS, list)
            assert len(config.CORS_ORIGINS) == 2
            assert "http://localhost:3000" in config.CORS_ORIGINS
            assert "https://example.com" in config.CORS_ORIGINS

    def test_api_config_multiple_origins(self):
        """Тест множественных источников CORS"""

        origins = [
            "https://frontend.example.com",
            "https://admin.example.com",
            "https://dashboard.example.com",
            "http://localhost:3000",
            "http://localhost:8080"
        ]

        config = MonitoringConfig(
            HOST="0.0.0.0",
            PORT=8000,
            DEBUG=False,
            CORS_ORIGINS=origins,
            CORS_ALLOW_CREDENTIALS=True,
            API_DOCS_ENABLED=True,
            API_TITLE="API",
            API_VERSION="1.0"
        )

        assert len(config.CORS_ORIGINS) == 5
        for origin in origins:
            assert origin in config.CORS_ORIGINS
