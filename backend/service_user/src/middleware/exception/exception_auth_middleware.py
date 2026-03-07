""" Middleware для обработки исключений """

from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import InvalidCredentialsException, InvalidTokenException


def _create_error_response(
    message: str,
    status_code: int,
    error_code: str
) -> dict:
    """Создаёт структурированный ответ об ошибке"""
    return {
        "error": {
            "message": message,
            "code": error_code,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки исключений"""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except InvalidCredentialsException:
            return JSONResponse(
                status_code=401,
                content=_create_error_response(
                    message="Неверные учетные данные!",
                    status_code=401,
                    error_code="INVALID_CREDENTIALS"
                )
            )
        except InvalidTokenException:
            return JSONResponse(
                status_code=401,
                content=_create_error_response(
                    message="Неверный или истёкший токен!",
                    status_code=401,
                    error_code="INVALID_TOKEN"
                )
            )
        except Exception:
            # Неизвестная ошибка
            return JSONResponse(
                status_code=500,
                content=_create_error_response(
                    message="Внутренняя ошибка сервера",
                    status_code=500,
                    error_code="INTERNAL_ERROR"
                )
            )
