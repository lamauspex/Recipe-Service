"""
Утилиты для работы с trace_id

Предоставляет единый источник истинности для trace_id
через ContextVar для корректной работы в async контекстах.
"""

from __future__ import annotations

import uuid
from fastapi import Request
from contextvars import ContextVar
from typing import Optional


# Контекстная переменная для trace_id (доступна во всех async контекстах)
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def get_trace_id(request: Optional[Request] = None) -> str:
    """
    Получение или создание trace_id

    Args:
        request: FastAPI Request (опционально)

    Returns:
        str: Уникальный trace_id
    """
    # Проверяем контекстную переменную
    current = trace_id_var.get()
    if current:
        return current

    # Проверяем заголовки запроса
    if request:
        existing = request.headers.get("X-Trace-ID")
        if existing:
            trace_id_var.set(existing)
            return existing

    # Генерируем новый
    new_trace_id = str(uuid.uuid4())[:12]
    trace_id_var.set(new_trace_id)
    return new_trace_id


def set_trace_id(trace_id: str) -> None:
    """
    Установка trace_id в контекст

    Args:
        trace_id: Trace ID для установки
    """
    trace_id_var.set(trace_id)


def clear_trace_id() -> None:
    """Очистка trace_id из контекста"""
    trace_id_var.set(None)
