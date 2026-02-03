"""
Обработчики исключений

"""

from __future__ import annotations


from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException, RequestValidationError

from backend.user_service.src.exceptions.base import AppException
from backend.user_service.src.exceptions.handlers import ErrorHandler


class ExceptionHandlers:
    """
    FastAPI Обработчики исключений
    """

    @staticmethod
    async def http_exception_handler(
        request: Request,
        exc: HTTPException
    ) -> JSONResponse:
        """Обработка HTTPException FastAPI"""

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.detail if hasattr(exc, 'detail')
                    else "HTTP Error",
                    "code": "HTTP_ERROR",
                    "status_code": exc.status_code
                }
            }
        )

    @staticmethod
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """Обработка RequestValidationError"""

        errors = exc.errors()
        error_details = []
        for error in errors:
            error_details.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })

        # Очищаем ошибки от несериализуемых объектов
        # (например, ValueError в ctx)
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif hasattr(obj, "__dict__"):
                return str(obj)
            else:
                return obj

        clean_errors = make_serializable(errors)

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "message": "Ошибка валидации данных",
                    "code": "VALIDATION_ERROR",
                    "status_code": 422,
                    "details": {
                        "field_errors": clean_errors
                    }
                }
            }
        )

    @staticmethod
    async def app_exception_handler(
        request: Request,
        exc: AppException
    ) -> JSONResponse:
        """Обработка кастомных AppException"""

        error_dict = exc.to_dict()
        return JSONResponse(
            status_code=error_dict["error"]["status_code"],
            content=error_dict,
        )

    @staticmethod
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Обработка неожиданных исключений"""

        error_handler = ErrorHandler()
        error_response = error_handler.handle(exc)

        return JSONResponse(
            status_code=error_response["error"]["status_code"],
            content=error_response,
        )


def setup_exception_handlers(app) -> None:
    """Настройка всех обработчиков исключений"""

    exception_handlers = ExceptionHandlers()

    app.add_exception_handler(
        HTTPException,
        exception_handlers.http_exception_handler
    )
    app.add_exception_handler(
        RequestValidationError,
        exception_handlers.validation_exception_handler
    )
    app.add_exception_handler(
        AppException,
        exception_handlers.app_exception_handler
    )
    app.add_exception_handler(
        Exception,
        exception_handlers.unhandled_exception_handler
    )
