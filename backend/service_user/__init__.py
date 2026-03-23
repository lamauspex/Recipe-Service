"""
User Service - Сервис управления пользователями

Основные компоненты:
- Сервисы бизнес-логики (AuthService, RegisterService)
- API эндпоинты для аутентификации и регистрации
- Репозитории для работы с БД
"""

from .src.app_users import create_app
from .src.infrastructure.container import container, Container

__all__ = [
    "create_app",
    "container",
    "Container",
]
