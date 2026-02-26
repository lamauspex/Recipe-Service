""" Базовый конфигурационный класс """


from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """ Базовый конфигурационный класс """

    model_config = SettingsConfigDict(
        env_file=r"backend/service_user/.env",
        extra='ignore',
        env_prefix="USER_SERVICE_",
        validate_assignment=True,
    )
