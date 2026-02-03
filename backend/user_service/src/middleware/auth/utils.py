"""Вспомогательные функции для авторизации"""

from typing import Optional, List

from backend.user_service.src.models import User


def extract_user_from_context(*args, **kwargs) -> Optional[User]:
    """Извлечение пользователя из контекста функции"""

    # Поиск в позиционных аргументах
    for arg in args:
        if isinstance(arg, User):
            return arg

    # Поиск в именованных аргументах
    return kwargs.get('current_user')


def safe_user_check(user: Optional[User]) -> bool:
    """Безопасная проверка пользователя"""

    return user is not None and hasattr(user, 'is_active')


def format_permission_error(
    missing_permissions: List[str],
    required: List[str]
) -> dict:
    """Форматирование ошибки для отсутствующих разрешений"""

    return {
        "message": "Недостаточно прав",
        "missing_permissions": missing_permissions,
        "required_permissions": required
    }


def create_auth_error_response(message: str, status_code: int = 403) -> dict:
    """Создание стандартного ответа об ошибке авторизации"""

    return {
        "message": message,
        "status_code": status_code,
        "error_type": "AUTHORIZATION_ERROR"
    }
