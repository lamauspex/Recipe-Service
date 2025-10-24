"""
Обработчики исключений для user-service
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exceptions import HTTPException
import traceback
import logging

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Настройка обработчиков исключений для приложения"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Обработчик HTTP исключений"""
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "status_code": exc.status_code,
                    "message": exc.detail,
                    "type": "HTTP_ERROR"
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        """Обработчик исключений валидации запросов"""
        logger.warning(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "status_code": 422,
                    "message": "Ошибка валидации данных",
                    "details": exc.errors(),
                    "type": "VALIDATION_ERROR"
                }
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Обработчик всех остальных исключений"""
        logger.error(f"Unhandled exception: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "status_code": 500,
                    "message": "Внутренняя ошибка сервера",
                    "type": "INTERNAL_ERROR"
                }
            }
        )
