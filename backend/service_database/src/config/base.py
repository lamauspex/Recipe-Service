"""
Базовый конфигурационный класс для Database Service

Использует pydantic-settings для загрузки конфигурации из переменных окружения.
Все переменные окружения должны иметь префикс DATABASE_SERVICE_

"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class DBBaseConfig(BaseSettings):
    """
    Базовый конфигурационный класс для Database Service

    Загружает настройки из переменных окружения с префиксом DATABASE_SERVICE_.
    Использует pydantic для валидации и типизации.

    """

    model_config = SettingsConfigDict(

        # Путь к .env файлу относительно корня проекта
        env_file=r"backend/service_database/.env",

        # Игнорировать лишние переменные окружения
        extra='ignore',

        # Префикс для всех переменных окружения
        env_prefix="DATABASE_SERVICE_",

        # Валидировать значения при присваивании атрибутов
        validate_assignment=True,
    )
