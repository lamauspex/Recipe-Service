# Сервисный слой нового поколения
"""
Новый сервисный слой, построенный по принципам Clean Architecture:

- interfaces/ - Интерфейсы сервисов
- usecases/ - Бизнес-логика (сценарии использования)
- dto/ - Data Transfer Objects
- ports/ - Порт-адаптер паттерн (интерфейсы к внешним системам)
- infrastructure/ - Реализации (адаптеры)
- decorators/ - Декораторы для cross-cutting concerns
"""

from .interfaces.auth import AuthInterface
from .interfaces.user import UserInterface
from .interfaces.security import SecurityInterface
from .interfaces.admin import AdminInterface

from .di_container import (
    get_auth_service,
    get_security_service,
    get_user_repository,
    get_token_repository
)

__all__ = [
    "AuthInterface",
    "UserInterface", 
    "SecurityInterface",
    "AdminInterface",
    "get_auth_service",
    "get_security_service",
    "get_user_repository",
    "get_token_repository"
]