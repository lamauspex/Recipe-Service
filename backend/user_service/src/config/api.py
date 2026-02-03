""" Основная конфигурация """

from pydantic import Field

from .base import BaseConfig


class ApiConfig(BaseConfig):
    """Конфигурация API"""

    # СЕРВЕР
    HOST: str = Field(description="Хост для запуска")
    PORT: int = Field(description="Порт сервиса")
    ENVIRONMENT: str = Field(description="Среда работы")

    # API ДОКУМЕНТАЦИЯ
    API_DOCS_ENABLED: bool = Field(description="Включить документацию API")
    API_DESCRIPTION: str = Field(description="Описание API")
    API_TITLE: str = Field(description="Заголовок API")
    API_VERSION: str = Field(description="Версия API")


api_config = ApiConfig()
