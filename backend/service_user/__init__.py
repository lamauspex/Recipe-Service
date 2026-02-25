"""
User Service - Сервис управления пользователями

Основные компоненты:
- Сервисы бизнес-логики (AuthService, RegisterService)
- API эндпоинты для аутентификации и регистрации
- Репозитории для работы с БД
"""

from .app_users import app_users, create_app
from .src.container import container, Container

__all__ = [
    "app_users",
    "create_app",
    "container",
    "Container",
]
