""" Базовый конфигурационный класс """


from pydantic_settings import BaseSettings, SettingsConfigDict


class DBBaseConfig(BaseSettings):
    """ Базовый конфигурационный класс """

    model_config = SettingsConfigDict(
        env_file=r"backend/database_service/.env",
        extra='ignore',
        env_prefix="DATABASE_SERVICE",
        validate_assignment=True,
    )
