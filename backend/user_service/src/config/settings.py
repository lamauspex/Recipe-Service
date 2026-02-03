""" Центральный объект конфигурации для user_service """


from ..config import (
    monitoring_config,
    cache_config,
    api_config,
    auth_config,
)
from backend.database_service.database import database_config


class _SettingsHolder:
    """ Холдер для синглтона """

    instance = None


class Settings:
    """ Центральный объект конфигурации для user_service """

    def __new__(cls):
        if _SettingsHolder.instance is None:
            _SettingsHolder.instance = super().__new__(cls)
            _SettingsHolder.instance._initialized = False
        return _SettingsHolder.instance

    def __init__(self):
        # Инициализируем только один раз
        if self._initialized:
            return

        self.auth = auth_config
        self.database = database_config
        self.api = api_config
        self.cache = cache_config
        self.monitoring = monitoring_config

        self._initialized = True


settings = Settings()
