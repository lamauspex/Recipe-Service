""" Базовый конфигурационный класс """


from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseRConfig(BaseSettings):
    """ Базовый конфигурационный класс """

    model_config = SettingsConfigDict(
        env_file=r"backend/service_recipe/.env",
        extra='ignore',
        env_prefix="RECIPE_SERVICE_",
        validate_assignment=True
    )
