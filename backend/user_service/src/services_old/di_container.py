"""
Современный DI-контейнер для управления зависимостями сервисов
Обеспечивает удобство использования и тестируемость
"""


from typing import Dict, Any, Type, TypeVar, Callable
from functools import wraps


T = TypeVar('T')


class ServiceContainer:
    """
    Современный DI-контейнер для управления сервисами и их зависимостями.

    Особенности:
    - Автоматическое разрешение зависимостей
    - Поддержка синглтонов
    - Простой API
    - Валидация зависимостей
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._is_initialized = False

    def register_singleton(self, name: str, service_class: Type[T], *args, **kwargs) -> None:
        """Регистрация сервиса как синглтон"""
        self._factories[name] = lambda: service_class(*args, **kwargs)

    def register_factory(self, name: str, factory: Callable[[], T]) -> None:
        """Регистрация фабрики для создания сервисов"""
        self._factories[name] = factory

    def register_instance(self, name: str, instance: T) -> None:
        """Регистрация готового экземпляра сервиса"""
        self._services[name] = instance
        self._singletons[name] = instance

    def get(self, name: str) -> Any:
        """Получение сервиса из контейнера"""
        if name in self._singletons:
            return self._singletons[name]

        if name not in self._factories:
            raise ValueError(
                f"Сервис '{name}' не зарегистрирован в контейнере")

        # Создаем экземпляр
        instance = self._factories[name]()

        # Если это синглтон, сохраняем
        if hasattr(instance, '_is_singleton') and instance._is_singleton:
            self._singletons[name] = instance

        return instance

    def has(self, name: str) -> bool:
        """Проверка наличия сервиса в контейнере"""
        return name in self._services or name in self._singletons or name in self._factories

    def initialize(self, db_session, config=None) -> None:
        """Инициализация всех сервисов с зависимостями"""
        if self._is_initialized:

            return

        try:
            # Регистрируем общие зависимости
            self._register_common_dependencies(db_session, config)

            # Регистрируем сервисы аутентификации
            self._register_auth_services(db_session, config)

            # Регистрируем сервисы пользователей
            self._register_user_services(db_session, config)

            # Регистрируем сервисы безопасности
            self._register_security_services(db_session, config)

            # Регистрируем административные сервисы
            self._register_admin_services(db_session, config)

            self._is_initialized = True

        except Exception as e:

            raise

    def _register_common_dependencies(self, db_session, config) -> None:
        """Регистрация общих зависимостей"""
        # Базовая конфигурация
        self.register_instance('config', config or {})
        self.register_instance('db_session', db_session)

        # Общие утилиты
        from common.base_service import BaseService
        from common.password_utility import password_utility
        from common.response_builder import ResponseBuilder
        from common.rate_limit_utility import RateLimitUtility

        self.register_instance('base_service_class', BaseService)
        self.register_instance('password_utility', password_utility)
        self.register_instance('response_builder', ResponseBuilder)
        self.register_instance('rate_limit_utility_class', RateLimitUtility)

    def _register_auth_services(self, db_session, config) -> None:
        """Регистрация сервисов аутентификации"""
        from auth_service.password_service import PasswordService
        from auth_service.jwt_service import JWTService
        from auth_service.refresh_token_service import RefreshTokenService
        from auth_service.auth_service import AuthService
        from backend.user_service.src.repository import (
            UserRepository,
            RefreshTokenRepository
        )

        # Базовые сервисы
        self.register_singleton('password_service', PasswordService)
        self.register_singleton('jwt_service', JWTService, config)

        # Репозитории
        self.register_factory(
            'user_repository', lambda: UserRepository(db_session))
        self.register_factory('refresh_token_repository',
                              lambda: RefreshTokenRepository(db_session))

        # Сервисы с зависимостями
        self.register_factory('refresh_token_service',
                              lambda: RefreshTokenService(db_session))

        self.register_factory('auth_service',
                              lambda: AuthService(
                                  db_session,
                                  self.get('jwt_service'),
                                  self.get('password_service'),
                                  self.get('refresh_token_service')
                              ))

    def _register_user_services(self, db_session, config) -> None:
        """Регистрация сервисов пользователей"""
        from user_service.service_layer import UserService
        from user_service.register_user import RegisterService
        from backend.user_service.src.repository import UserRepository

        self.register_factory('user_service',
                              lambda: UserService(db_session))

        self.register_factory('register_service',
                              lambda: RegisterService(db_session))

    def _register_security_services(self, db_session, config) -> None:
        """Регистрация сервисов безопасности"""
        from security_service.account_locker import AccountLocker
        from security_service.ip_blocker import IpBlocker
        from security_service.rate_limiter import RateLimiter
        from security_service.suspicious_detector import SuspiciousActivityDetector
        from security_service.security_service import SecurityService

        self.register_factory('account_locker',
                              lambda: AccountLocker(config, db_session))

        self.register_factory('ip_blocker',
                              lambda: IpBlocker(config))

        self.register_factory('rate_limiter',
                              lambda: RateLimiter(config, db_session))

        self.register_factory('suspicious_detector',
                              lambda: SuspiciousActivityDetector(config, db_session))

        self.register_factory('security_service',
                              lambda: SecurityService(config, db_session))

    def _register_admin_services(self, db_session, config) -> None:
        """Регистрация административных сервисов"""
        from admin_service.role_service import RoleService, UserRoleService, PermissionService
        from admin_service.managment_service import ManagementService
        from admin_service.statistic_service import StatisticService
        from admin_service.login_service import LoginService

        self.register_factory('role_service',
                              lambda: RoleService(db_session))

        self.register_factory('user_role_service',
                              lambda: UserRoleService(db_session))

        self.register_factory('permission_service',
                              lambda: PermissionService(db_session))

        self.register_factory('management_service',
                              lambda: ManagementService(db_session))

        self.register_factory('statistic_service',
                              lambda: StatisticService(db_session))

        self.register_factory('login_service',
                              lambda: LoginService(db_session))


# Глобальный экземпляр контейнера
container = ServiceContainer()


class ServiceLocator:
    """Удобный локатор сервисов для использования в приложении"""

    def __init__(self, container: ServiceContainer):
        self._container = container

    def get_auth_service(self):
        """Получение сервиса аутентификации"""
        return self._container.get('auth_service')

    def get_user_service(self):
        """Получение сервиса пользователей"""
        return self._container.get('user_service')

    def get_register_service(self):
        """Получение сервиса регистрации"""
        return self._container.get('register_service')

    def get_security_service(self):
        """Получение сервиса безопасности"""
        return self._container.get('security_service')

    def get_management_service(self):
        """Получение сервиса управления"""
        return self._container.get('management_service')

    def get_role_service(self):
        """Получение сервиса ролей"""
        return self._container.get('role_service')

    def get_user_role_service(self):
        """Получение сервиса ролей пользователей"""
        return self._container.get('user_role_service')

    def get_permission_service(self):
        """Получение сервиса разрешений"""
        return self._container.get('permission_service')

    def get_statistic_service(self):
        """Получение сервиса статистики"""
        return self._container.get('statistic_service')

    def get_login_service(self):
        """Получение сервиса входов"""
        return self._container.get('login_service')

    def get_password_service(self):
        """Получение сервиса паролей"""
        return self._container.get('password_service')

    def get_jwt_service(self):
        """Получение JWT сервиса"""
        return self._container.get('jwt_service')

    def get(self, service_name: str):
        """Получение сервиса по имени"""
        return self._container.get(service_name)


# Функция для быстрой инициализации
def init_services(db_session, config=None) -> ServiceLocator:
    """Быстрая инициализация всех сервисов"""
    container.initialize(db_session, config)
    return ServiceLocator(container)


# Декоратор для автоматического получения сервисов
def inject_service(service_name: str):
    """Декоратор для автоматического внедрения зависимостей"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Получаем сервис из контейнера
            service = container.get(service_name)

            # Добавляем сервис в аргументы функции
            kwargs[service_name] = service

            return func(*args, **kwargs)
        return wrapper
    return decorator
