""" Конфигурация БД """


from pydantic import Field

from .base import DBBaseConfig


class DataBaseConfig(DBBaseConfig):
    """ Конфигурация БД """

    # БАЗА ДАННЫХ (ОБЩИЕ НАСТРОЙКИ)
    POSTGRES_USER: str = Field(description="Пользователь")
    DB_HOST: str = Field(description="Хост БД")
    DB_PORT: int = Field(description="Порт БД")
    POSTGRES_DB: str = Field(description="Название БД")
    POSTGRES_PASSWORD: str = Field(description="Пароль БД")
    DB_DRIVER: str = Field(description="Драйвер БД")
    # ОКРУЖЕНИЕ И РЕЖИМ ОТЛАДКИ
    TESTING: bool = Field(description="Тестирование")
    DEBUG: bool = Field(description="Режим отладки")
    # Настройки пула соединений
    POOL_SIZE: int = Field(description="Размер пула соединений")
    MAX_OVERFLOW: int = Field(description="Максимальный перелив")

    def get_database_url(self) -> str:
        """
        Получить URL базы данных с указанным драйвером
        """

        if self.TESTING:
            return "sqlite:///:memory:"

        return (
            f"{self.DB_DRIVER}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )
