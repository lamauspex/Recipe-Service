"""
CORS headers

Функции для добавления CORS заголовков
"""

from typing import List
from fastapi import Request
from starlette.responses import Response


class CORSConfig:
    """Конфигурация CORS"""

    def __init__(
        self,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = True,
        max_age: int = 86400
    ):
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or [
            "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"
        ]
        self.allow_headers = allow_headers or [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Trace-ID"
        ]
        self.allow_credentials = allow_credentials
        self.max_age = max_age


# Глобальная конфигурация CORS
_cors_config = CORSConfig()


def set_cors_config(config: CORSConfig) -> None:
    """Установка конфигурации CORS"""
    global _cors_config
    _cors_config = config


def get_cors_config() -> CORSConfig:
    """Получение конфигурации CORS"""
    return _cors_config


def add_cors_headers(response: Response, request: Request) -> Response:
    """
    Добавление CORS заголовков к ответу

    Args:
        response: FastAPI Response
        request: FastAPI Request

    Returns:
        Response: Response с добавленными CORS заголовками
    """
    config = get_cors_config()

    # Получаем origin из запроса
    origin = request.headers.get("origin")

    # Проверяем, разрешен ли origin
    if origin and _is_origin_allowed(origin, config.allow_origins):
        response.headers["Access-Control-Allow-Origin"] = origin
        if config.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"

    # Добавляем заголовки для preflight запросов
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = ", ".join(
            config.allow_methods
        )
        response.headers["Access-Control-Allow-Headers"] = ", ".join(
            config.allow_headers
        )
        response.headers["Access-Control-Max-Age"] = str(config.max_age)

    return response


def _is_origin_allowed(origin: str, allowed_origins: List[str]) -> bool:
    """
    Проверка, разрешен ли origin

    Args:
        origin: Origin из запроса
        allowed_origins: Список разрешенных origins

    Returns:
        bool: Разрешен ли origin
    """
    if "*" in allowed_origins:
        return True

    return origin in allowed_origins


def create_cors_response(
    methods: List[str] = None,
    headers: List[str] = None,
    origin: str = "*"
) -> Response:
    """
    Создание CORS ответа для preflight запроса

    Args:
        methods: Разрешенные методы
        headers: Разрешенные заголовки
        origin: Origin для заголовка

    Returns:
        Response: Пустой Response с CORS заголовками
    """
    config = get_cors_config()

    response = Response()
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = ", ".join(
        methods or config.allow_methods
    )
    response.headers["Access-Control-Allow-Headers"] = ", ".join(
        headers or config.allow_headers
    )
    response.headers["Access-Control-Max-Age"] = str(config.max_age)

    return response
