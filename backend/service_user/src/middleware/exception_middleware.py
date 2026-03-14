""" Middleware для обработки исключений """

from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.service_user.src.exception import (
    AppException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
)
from backend.shared.logging import get_logger


logger = get_logger(__name__).bind(
    layer="exception",
    service="user"
)


def _error_response(message: str, status_code: int, code: str) -> dict:
    return {
        "error": {
            "message": message,
            "code": code,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        try:
            return await call_next(request)

        except InvalidCredentialsException:
            return JSONResponse(
                401,
                _error_response(
                    "Неверные учетные данные!",
                    401, "INVALID_CREDENTIALS"
                ))

        except (InvalidTokenException, TokenExpiredException):
            return JSONResponse(
                401,
                _error_response(
                    "Неверный или истёкший токен!",
                    401,
                    "INVALID_TOKEN"
                ))

        except AppException as exc:
            return JSONResponse(exc.status_code, exc.to_dict())

        except AppException as exc:
            logger.error("App exception", message=exc.message, code=exc.code)

        except Exception:
            return JSONResponse(
                500,
                _error_response(
                    "Внутренняя ошибка сервера",
                    500,
                    "INTERNAL_ERROR"
                ))
