"""
Тесты для базовой конфигурации BaseConfig
"""

import os
import pytest
import tempfile
from unittest.mock import patch
from pydantic import ValidationError

from user_service.config.base import BaseConfig


class ConfigForTesting(BaseConfig):
    """Тестовая конфигурация для проверки базового функционала"""

    test_string: str
    test_int: int
    test_bool: bool = False
    test_optional: str | None = None


def test_base_config_init():
    """Тест инициализации BaseConfig"""

    config = ConfigForTesting(
        test_string="test_value",
        test_int=42
    )

    assert config.test_string == "test_value"
    assert config.test_int == 42
    assert config.test_bool is False
    assert config.test_optional is None


def test_base_config_env_prefix():
    """Тест работы env_prefix"""

    with patch.dict(os.environ, {
        "USER_SERVICE_TEST_STRING": "from_env",
        "USER_SERVICE_TEST_INT": "123",
        "USER_SERVICE_TEST_BOOL": "true"
    }):
        config = ConfigForTesting()

        assert config.test_string == "from_env"
        assert config.test_int == 123
        assert config.test_bool is True


def test_base_config_extra_ignore():
    """Тест extra='ignore' - игнорирование дополнительных полей"""

    with patch.dict(os.environ, {
        "USER_SERVICE_TEST_STRING": "test",
        "USER_SERVICE_UNKNOWN_FIELD": "should_be_ignored",
        "USER_SERVICE_ANOTHER_FIELD": "123"
    }):
        config = ConfigForTesting(test_int=42)

        # Дополнительные поля должны быть проигнорированы
        assert config.test_string == "test"
        assert config.test_int == 42
        assert not hasattr(config, 'unknown_field')
        assert not hasattr(config, 'another_field')


def test_base_config_validate_assignment():
    """Тест validate_assignment=True"""

    config = ConfigForTesting(
        test_string="initial",
        test_int=10
    )

    # Корректное присваивание должно работать
    config.test_string = "updated"
    config.test_int = 20
    assert config.test_string == "updated"
    assert config.test_int == 20

    # Некорректное присваивание должно вызвать ошибку
    with pytest.raises(ValidationError):
        config.test_int = "not_an_int"

    with pytest.raises(ValidationError):
        config.test_bool = "not_a_bool"


def test_base_config_env_file():
    """Тест загрузки из env файла"""

    # Создаем временный env файл
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.env',
        delete=False
    ) as f:
        f.write("USER_SERVICE_TEST_STRING=from_file\n")
        f.write("USER_SERVICE_TEST_INT=999\n")
        f.write("USER_SERVICE_TEST_BOOL=true\n")
        env_file_path = f.name

    try:
        # Создаем конфигурацию с указанием env файла
        class FileConfig(BaseConfig):
            model_config = {
                'env_file': env_file_path,
                'env_prefix': 'USER_SERVICE_',
                'extra': 'ignore',
                'validate_assignment': True
            }

            test_string: str
            test_int: int
            test_bool: bool = False

        config = FileConfig()

        assert config.test_string == "from_file"
        assert config.test_int == 999
        assert config.test_bool is True

    finally:
        # Удаляем временный файл
        os.unlink(env_file_path)


def test_base_config_type_validation():
    """Тест валидации типов"""

    # Корректные типы
    config = ConfigForTesting(
        test_string="valid_string",
        test_int=42,
        test_bool=True
    )
    assert config.test_string == "valid_string"
    assert config.test_int == 42
    assert config.test_bool is True

    # Некорректные типы должны вызвать ошибку
    with pytest.raises(ValidationError):
        ConfigForTesting(
            test_string="valid",
            test_int="not_an_int"  # Должно быть int
        )

    with pytest.raises(ValidationError):
        ConfigForTesting(
            test_string="valid",
            test_int=42,
            test_bool="not_a_bool"  # Должно быть bool
        )


def test_base_config_default_values():
    """Тест значений по умолчанию"""

    config = ConfigForTesting(
        test_string="test",
        test_int=100
    )

    # Проверяем значения по умолчанию
    assert config.test_bool is False
    assert config.test_optional is None


def test_base_config_inheritance():
    """Тест наследования от BaseConfig"""

    # Создаем конфигурацию без явного указания model_config
    class SimpleConfig(BaseConfig):
        simple_field: str = "default"

    config = SimpleConfig()
    assert config.simple_field == "default"

    # Проверяем, что базовые настройки применились
    assert config.model_config['env_prefix'] == 'USER_SERVICE_'
    assert config.model_config['extra'] == 'ignore'
    assert config.model_config['validate_assignment'] is True


def test_base_config_env_override():
    """Тест переопределения значений из env переменных"""

    with patch.dict(os.environ, {
        "USER_SERVICE_TEST_STRING": "env_value",
        "USER_SERVICE_TEST_INT": "777"
    }):
        # Создаем конфигурацию с явными значениями
        config = ConfigForTesting(
            test_string="explicit_value",
            test_int=555
        )

        # Env переменные должны переопределить явные значения
        assert config.test_string != "env_value"
        assert config.test_int != 777
