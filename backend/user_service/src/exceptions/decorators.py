"""
Декораторы и утилиты для обработки исключений

"""

from __future__ import annotations

from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, TypeVar

from .handlers import error_handler

# Type variable для generic функций
F = TypeVar('F', bound=Callable[..., Any])


def exception_handler(func: F) -> F:
    """
    Декоратор для автоматической обработки исключений в функциях
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            return error_handler.handle(exc)

    return wrapper


@contextmanager
def safe_execution(default_return: Any = None):
    """
    Контекстный менеджер для безопасного выполнения кода
    """
    try:
        yield
    except Exception as exc:
        result = error_handler.handle(exc)
        if isinstance(result, dict) and "error" in result:
            # Возвращаем информацию об ошибке
            yield result
            return
        # Возвращаем значение по умолчанию
        yield default_return
