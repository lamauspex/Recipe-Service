"""Advanced Security Middleware

Расширенный middleware для безопасности
"""

from __future__ import annotations

import re
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from user_service.config import settings
from user_service.exceptions.convenience import rate_limited

from .cors import add_cors_headers
from .headers import add_security_headers
from .rate_limiting import get_rate_limiter
from .._utils import get_client_ip


class AdvancedSecurityMiddleware(BaseHTTPMiddleware):
    """
    Расширенный middleware для безопасности

    Функции:
    - Rate limiting
    - CORS
    - Security headers
    - Блокировка подозрительных IP
    - Защита от SQL Injection
    - Обнаружение подозрительных паттернов
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("security")
        self.rate_limiter = get_rate_limiter()

        # Паттерны для обнаружения атак
        self._suspicious_patterns = {
            "sql_injection": re.compile(
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b.*?"
                r"(\bFROM\b|\bWHERE\b|\bINTO\b|\bTABLE\b|\bDATABASE\b))|"
                r"(--|;|'|\"|%27|%22|/\*|\*/|@@|@)",
                re.IGNORECASE
            ),
            "xss": re.compile(
                r"(<script|javascript:|vbscript:|data:text/html|on\w+\s*=)",
                re.IGNORECASE
            ),
            "path_traversal": re.compile(
                r"(\.\./|\.\.\\|%2e%2e/|%2e%2e\\|\\\0|/)"
            ),
            "command_injection": re.compile(
                r"(;|\||`|\$\(|\$\{.*\})"
            )
        }

        # Подозрительные User-Agent
        self._suspicious_agents = [
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "burp",
            "owasp",
            "wpscan",
            "havij",
            "acunetix"
        ]

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Основной метод middleware"""

        client_ip = get_client_ip(request)
        user_agent = request.headers.get("user-agent", "").lower()

        # 1. Проверка rate limiting
        is_allowed, rate_info = self.rate_limiter.is_allowed(client_ip)
        if not is_allowed:
            self.logger.warning(f"Rate limit exceeded for IP {client_ip}")
            raise rate_limited(
                message="Слишком много запросов. Попробуйте позже.",
                retry_after=rate_info.get("blocked_seconds_remaining", 60)
            )

        # 2. Проверка подозрительной активности
        self._check_suspicious_activity(request, client_ip, user_agent)

        # 3. Проверка Suspicious IP
        if self._is_suspicious_ip(client_ip):
            self.logger.warning(f"Suspicious IP detected: {client_ip}")

        # 4. Вызов следующего обработчика
        response = await call_next(request)

        # 5. Добавляем заголовки
        response = add_cors_headers(response, request)
        response = add_security_headers(response)

        # 6. Логируем запрос
        self._log_security_event(request, client_ip, response.status_code)

        return response

    def _check_suspicious_activity(
        self,
        request: Request,
        client_ip: str,
        user_agent: str
    ) -> None:
        """Проверка подозрительной активности"""

        # Проверяем User-Agent
        for suspicious_agent in self._suspicious_agents:
            if suspicious_agent in user_agent:
                self.logger.warning(
                    f"Suspicious User-Agent detected: {user_agent}")

        # Проверяем паттерны в URL
        url_path = str(request.url.path)
        for pattern_name, pattern in self._suspicious_patterns.items():
            if pattern.search(url_path):
                self.logger.warning(
                    f"Suspicious pattern '{pattern_name}' in URL: {url_path} "
                    f"from IP {client_ip}"
                )

        # Проверяем query parameters
        for key, value in request.query_params.items():
            if isinstance(value, str):
                for pattern_name, pattern in self._suspicious_patterns.items():
                    if pattern.search(value):
                        self.logger.warning(
                            f"Suspicious pattern '{pattern_name}' in query param "
                            f"'{key}': {value} from IP {client_ip}"
                        )

    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Проверка, является ли IP подозрительным"""
        if ip_address.startswith("127.") or ip_address == "localhost":
            if settings.ENVIRONMENT == "production":
                return True
        return False

    def _log_security_event(
        self,
        request: Request,
        client_ip: str,
        status_code: int
    ) -> None:
        """Логирование события безопасности"""
        self.logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"IP: {client_ip} - Status: {status_code}"
        )


class SimpleSecurityMiddleware(BaseHTTPMiddleware):
    """
    Простой middleware для безопасности

    Функции:
    - CORS
    - Security headers
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("security")

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """Основной метод middleware"""

        response = await call_next(request)
        response = add_cors_headers(response, request)
        response = add_security_headers(response)
        return response
