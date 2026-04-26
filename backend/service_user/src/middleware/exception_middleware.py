""" Middleware для обработки исключений """

from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.shared.logging import get_logger
from backend.service_user.src.exception import (
    AppException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException,
)


logger = get_logger(__name__).bind(
    layer="exception",
    service="user"
)


def _error_response(
    message: str,
    status_code: int,
    code: str
) -> dict:
    return {
        "error": {
            "message": message,
            "code": code,
            "status_code": status_code,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        try:
            return await call_next(request)

        except InvalidCredentialsException:
            return JSONResponse(
                status_code=401,
                content=_error_response(
                    "Неверные учетные данные!",
                    401, "INVALID_CREDENTIALS"
                ))

        except (InvalidTokenException, TokenExpiredException):
            return JSONResponse(
                status_code=401,
                content=_error_response(
                    "Неверный или истёкший токен!",
                    401,
                    "INVALID_TOKEN"
                ))

        except AppException as exc:
            logger.error(
                "App exception",
                message=exc.message,
                code=exc.code
            )
            return JSONResponse(
                status_code=exc.status_code,
                content=exc.to_dict()
            )

        except Exception as exc:
            logger.exception(
                "Unhandled exception",
                error=str(exc),
                error_type=type(exc).__name__
            )
            return JSONResponse(
                status_code=500,
                content=_error_response(
                    "Внутренняя ошибка сервера",
                    500,
                    "INTERNAL_ERROR"
                ))
