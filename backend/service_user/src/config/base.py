""" Базовый конфигурационный класс """


from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """ Базовый конфигурационный класс """

    model_config = SettingsConfigDict(
        env_file=r".env",
        extra='ignore',
        env_prefix="USER_SERVICE_",
        validate_assignment=True,
    )
