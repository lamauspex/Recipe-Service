"""
Тесты для UUIDTypeDecorator
"""


from uuid import UUID, uuid4
from unittest.mock import MagicMock
from sqlalchemy import String

from user_service.models.decorator.type_decorator import UUIDTypeDecorator


def test_uuid_type_decorator_init():
    """Тест инициализации UUIDTypeDecorator"""

    decorator = UUIDTypeDecorator()

    assert isinstance(decorator.impl, String)
    assert decorator.cache_ok is True


def test_uuid_type_decorator_load_dialect_impl_postgresql():
    """Тест загрузки диалекта PostgreSQL"""

    decorator = UUIDTypeDecorator()

    # Мокаем PostgreSQL диалект
    mock_dialect = MagicMock()
    mock_dialect.name = 'postgresql'

    impl = decorator.load_dialect_impl(mock_dialect)

    # Проверяем, что возвращается PostgreSQL UUID тип
    assert hasattr(impl, 'as_uuid')


def test_uuid_type_decorator_load_dialect_impl_sqlite():
    """Тест загрузки диалекта SQLite"""

    decorator = UUIDTypeDecorator()

    # Мокаем SQLite диалект
    mock_dialect = MagicMock()
    mock_dialect.name = 'sqlite'
    # Настраиваем mock, чтобы он возвращал реальный String объект
    mock_dialect.type_descriptor.return_value = String(36)
    impl = decorator.load_dialect_impl(mock_dialect)

    # Проверяем, что возвращается String тип
    assert isinstance(impl, String)


def test_uuid_type_decorator_process_bind_param_postgresql():
    """Тест обработки параметров для PostgreSQL"""

    decorator = UUIDTypeDecorator()

    mock_dialect = MagicMock()
    mock_dialect.name = 'postgresql'

    test_uuid = uuid4()

    # Тест с валидным UUID
    result = decorator.process_bind_param(test_uuid, mock_dialect)
    assert result == test_uuid

    # Тест с None
    result = decorator.process_bind_param(None, mock_dialect)
    assert result is None


def test_uuid_type_decorator_process_bind_param_sqlite():
    """Тест обработки параметров для SQLite"""

    decorator = UUIDTypeDecorator()

    mock_dialect = MagicMock()
    mock_dialect.name = 'sqlite'

    test_uuid = uuid4()

    # Тест с валидным UUID
    result = decorator.process_bind_param(test_uuid, mock_dialect)
    assert result == str(test_uuid)

    # Тест с None
    result = decorator.process_bind_param(None, mock_dialect)
    assert result is None


def test_uuid_type_decorator_process_result_value_postgresql():
    """Тест обработки результатов для PostgreSQL"""

    decorator = UUIDTypeDecorator()

    mock_dialect = MagicMock()
    mock_dialect.name = 'postgresql'

    test_uuid = uuid4()

    # Тест с валидным UUID
    result = decorator.process_result_value(test_uuid, mock_dialect)
    assert result == test_uuid
    assert isinstance(result, UUID)

    # Тест с None
    result = decorator.process_result_value(None, mock_dialect)
    assert result is None


def test_uuid_type_decorator_process_result_value_sqlite():
    """Тест обработки результатов для SQLite"""

    decorator = UUIDTypeDecorator()

    mock_dialect = MagicMock()
    mock_dialect.name = 'sqlite'

    test_uuid = uuid4()
    uuid_string = str(test_uuid)

    # Тест с валидной строкой UUID
    result = decorator.process_result_value(uuid_string, mock_dialect)
    assert isinstance(result, UUID)
    assert result == test_uuid

    # Тест с None
    result = decorator.process_result_value(None, mock_dialect)
    assert result is None


def test_uuid_type_decorator_unknown_dialect():
    """Тест обработки неизвестного диалекта"""

    decorator = UUIDTypeDecorator()

    # Мокаем неизвестный диалект
    mock_dialect = MagicMock()
    mock_dialect.name = 'unknown'

    test_uuid = uuid4()

    # Для неизвестного диалекта должен обрабатываться как SQLite
    result = decorator.process_bind_param(test_uuid, mock_dialect)
    assert result == str(test_uuid)

    uuid_string = str(test_uuid)
    result = decorator.process_result_value(uuid_string, mock_dialect)
    assert isinstance(result, UUID)
    assert result == test_uuid
