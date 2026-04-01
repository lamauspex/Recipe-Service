""" Конфигурация RABBITMQ """


from pydantic import Field

from backend.service_recipe.src.config.base import BaseRConfig


class RebbitConfig(BaseRConfig):

    RABBITMQ_USER: str = Field(description='')
    RABBITMQ_PASSWORD: str = Field(description='')
    RABBITMQ_VHOST: str = Field(description='')
    RABBITMQ_URL: str = Field(description='')
