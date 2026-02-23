"""
Middleware для автоматического логирования HTTP запросов
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog

from backend.shared.logging.logger import get_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования входящих запросов

    Автоматически логирует:
    - Метод и путь запроса
    - Статус ответа
    - Время выполнения
    - IP клиента

    Добавляет request_id в контекст для трассировки.
    """

    def __init__(
        self,
        app: ASGIApp,
        log_request_body: bool = False,
        log_response_body: bool = False,
    ):
        super().__init__(app)
        self.logger = get_logger(__name__).bind(layer="http")
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Генерируем уникальный ID запроса
        request_id = str(uuid.uuid4())[:8]

        # Добавляем request_id в контекст
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
        )

        # Фиксируем время старта
        start_time = time.perf_counter()

        # Подготовка данных для логирования
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query_params = dict(
            request.query_params) if request.query_params else {}

        # Логируем входящий запрос
        self.logger.info(
            "→ Request started",
            method=method,
            path=path,
            query=query_params if query_params else None,
            client=client_host,
        )

        # Выполняем запрос
        try:
            response = await call_next(request)
        except Exception as exc:
            # Логируем ошибку
            duration = time.perf_counter() - start_time
            self.logger.error(
                "Request failed",
                method=method,
                path=path,
                error=str(exc),
                duration=f"{duration:.3f}s",
                status_code=500,
            )
            raise

        # Вычисляем время выполнения
        duration = time.perf_counter() - start_time

        # Определяем статус и уровень логирования
        status_code = response.status_code
        if status_code < 400:
            level = "info"
            status = "success"
        elif status_code < 500:
            level = "warning"
            status = "warning"
        else:
            level = "error"
            status = "error"

        # Логируем ответ
        log_method = getattr(self.logger, level)
        log_method(
            "← Request completed",
            method=method,
            path=path,
            status_code=status_code,
            status=status,
            duration=f"{duration:.3f}s",
        )

        # Добавляем заголовок с request_id
        response.headers["X-Request-ID"] = request_id

        return response
