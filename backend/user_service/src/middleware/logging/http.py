"""
Middleware и логирование HTTP запросов/ответов
"""


from __future__ import annotations

import time
from datetime import datetime
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from user_service.config import settings
from user_service.exceptions.base import AppException
from user_service.middleware.logging.utils_trace_id import (
    get_trace_id,
    set_trace_id,
)
from user_service.middleware.logging.loggers import http_logger
from .._utils import get_client_ip


class HTTPLogger:
    """
    HTTP логирование запросов и ответов

    Соответствует принципу единственной ответственности (SRP):
    - Только логирование HTTP трафика
    """

    @staticmethod
    def log_request(
        request: Request,
        trace_id: str,
        body_size: Optional[int] = None
    ) -> None:
        """
        Логирование входящего запроса

        Args:
            request: FastAPI Request
            trace_id: Trace ID запроса
            body_size: Размер тела запроса
        """
        # Проверяем, включено ли логирование запросов
        if not settings.monitoring.ENABLE_REQUEST_LOGGING:
            return

        http_logger.info(
            "incoming_request",
            trace_id=trace_id,
            timestamp=datetime.utcnow().isoformat(),
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            query_params=dict(request.query_params) or None,
            client_ip=get_client_ip(request),
            user_agent=request.headers.get("user-agent"),
            content_type=request.headers.get("content-type"),
            content_length=body_size or request.headers.get("content-length"),
        )

    @staticmethod
    def log_response(
        response: Response,
        trace_id: str,
        process_time_ms: float,
        body_size: Optional[int] = None
    ) -> None:
        """
        Логирование ответа

        Args:
            response: FastAPI Response
            trace_id: Trace ID запроса
            process_time_ms: Время обработки в мс
            body_size: Размер тела ответа
        """
        # Проверяем, включено ли логирование запросов
        if not settings.monitoring.ENABLE_REQUEST_LOGGING:
            return

        http_logger.info(
            "outgoing_response",
            trace_id=trace_id,
            timestamp=datetime.utcnow().isoformat(),
            status_code=response.status_code,
            process_time_ms=round(process_time_ms, 2),
            content_type=response.headers.get("content-type"),
            content_length=body_size or response.headers.get("content-length"),
        )

    @staticmethod
    def log_error(
        request: Request,
        trace_id: str,
        error: Exception,
        process_time_ms: float
    ) -> None:
        """
        Логирование ошибки

        Args:
            request: FastAPI Request
            trace_id: Trace ID запроса
            error: Исключение
            process_time_ms: Время обработки в мс
        """
        # Проверяем, включено ли логирование запросов
        if not settings.monitoring.ENABLE_REQUEST_LOGGING:
            return

        error_data = {
            "trace_id": trace_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "client_ip": get_client_ip(request),
            "process_time_ms": round(process_time_ms, 2),
            "error_type": type(error).__name__,
            "error_message": str(error),
        }

        # Для AppException добавляем дополнительную информацию
        if isinstance(error, AppException):
            error_data["error_code"] = error.context.error_code
            error_data["error_details"] = error.context.details

        http_logger.error("request_error", **error_data)


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования HTTP запросов и ответов

    Использует HTTPLogger для централизованного логирования
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Получаем или создаём trace_id
        trace_id = get_trace_id(request)
        set_trace_id(trace_id)

        # Засекаем время начала обработки
        start_time = time.perf_counter()

        try:
            # Логируем запрос
            HTTPLogger.log_request(request, trace_id)

            # Вызываем следующий обработчик
            response = await call_next(request)

            # Вычисляем время обработки
            process_time_ms = (time.perf_counter() - start_time) * 1000

            # Логируем ответ
            HTTPLogger.log_response(response, trace_id, process_time_ms)

            # Добавляем trace_id в заголовки ответа
            response.headers["X-Trace-ID"] = trace_id

            return response

        except Exception as exc:
            process_time_ms = (time.perf_counter() - start_time) * 1000
            HTTPLogger.log_error(request, trace_id, exc, process_time_ms)
            raise
