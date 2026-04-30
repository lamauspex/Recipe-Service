"""
Middleware для логирования входящих запросов

Логирование:
- Метод, путь, статус ответа
- Duration запроса
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


from backend.shared.logging.logger import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для базового логирования входящих запросов
    """

    async def dispatch(self, request: Request, call_next):
        logger = get_logger(__name__).bind(
            layer="middleware",
            service="recipe"
        )

        start_time = time.time()

        try:
            response = await call_next(request)

            duration = time.time() - start_time
            logger.info(
                f"← {request.method} {request.url.path}",
                duration=f"{duration:.3f}s",
                status_code=response.status_code
            )

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"← {request.method} {request.url.path} FAILED",
                duration=f"{duration:.3f}s",
                error=str(e)
            )
            raise
