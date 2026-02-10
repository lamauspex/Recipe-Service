""" Центральный объект конфигурации для user_service """


from .api import api_config
from .auth import auth_config
from .cache import cache_config
from .monitoring import monitoring_config


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
        self.api = api_config
        self.cache = cache_config
        self.monitoring = monitoring_config

        self._initialized = True


settings = Settings()
