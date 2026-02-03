"""
Security headers

Функции для добавления security заголовков
"""

from starlette.responses import Response


# Security заголовки по умолчанию
DEFAULT_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Cache-Control": "no-store, no-cache, must-revalidate, private",
    "Pragma": "no-cache"
}


class SecurityHeadersConfig:
    """Конфигурация security заголовков"""

    def __init__(self, custom_headers: dict = None, enabled: bool = True):
        self.enabled = enabled
        self.headers = {**DEFAULT_SECURITY_HEADERS}
        if custom_headers:
            self.headers.update(custom_headers)

    def add_header(self, name: str, value: str) -> None:
        """Добавление кастомного заголовка"""
        self.headers[name] = value

    def remove_header(self, name: str) -> None:
        """Удаление заголовка"""
        self.headers.pop(name, None)

    def get_headers(self) -> dict:
        """Получение всех заголовков"""
        return self.headers.copy()


# Глобальная конфигурация
_security_config = SecurityHeadersConfig()


def set_security_config(config: SecurityHeadersConfig) -> None:
    """Установка конфигурации security заголовков"""
    global _security_config
    _security_config = config


def get_security_config() -> SecurityHeadersConfig:
    """Получение конфигурации security заголовков"""
    return _security_config


def add_security_headers(response: Response) -> Response:
    """
    Добавление security заголовков к ответу

    Args:
        response: FastAPI Response

    Returns:
        Response: Response с добавленными security заголовками
    """
    config = get_security_config()

    if config.enabled:
        for header_name, header_value in config.headers.items():
            response.headers[header_name] = header_value

    return response


def add_hsts_headers(response: Response, max_age: int = 31536000) -> Response:
    """
    Добавление HSTS заголовков

    Args:
        response: FastAPI Response
        max_age: Время в секундах (по умолчанию 1 год)

    Returns:
        Response: Response с HSTS заголовками
    """
    response.headers["Strict-Transport-Security"] = f"max-age={max_age}; includeSubDomains"
    return response


def add_csp_headers(
    response: Response,
    policy: str = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
) -> Response:
    """
    Добавление Content-Security-Policy заголовка

    Args:
        response: FastAPI Response
        policy: CSP политика

    Returns:
        Response: Response с CSP заголовком
    """
    response.headers["Content-Security-Policy"] = policy
    return response
