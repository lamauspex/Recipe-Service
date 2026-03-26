"""
Базовый конфигурационный класс для Database Service

Использует pydantic-settings для загрузки конфигурации из переменных окружения.

"""


from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path | None:
    """Ищет .env в нескольких местах"""
    # Места для поиска (в порядке приоритета)
    search_paths = [
        Path(__file__).parent.parent.parent /
        ".env",
        Path.cwd() / ".env"
    ]

    for path in search_paths:
        if path.exists():
            return path

    return None


class DBBaseConfig(BaseSettings):
    """
    Базовый конфигурационный класс для Database Service

    Загружает настройки из переменных окружения с префиксом DATABASE_SERVICE_.
    Использует pydantic для валидации и типизации.

    """

    model_config = SettingsConfigDict(

        # Путь к .env файлу относительно корня проекта
        env_file=find_env_file(),
        env_file_encoding="utf-8",
        # Игнорировать лишние переменные окружения
        extra='ignore',
        # Валидировать значения при присваивании атрибутов
        validate_assignment=True,
    )
