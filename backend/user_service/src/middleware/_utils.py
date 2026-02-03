"""
Утилиты для работы с HTTP

Общие функции, используемые в middleware
"""

from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    Получение IP адреса клиента с учетом прокси

    Args:
        request: FastAPI Request

    Returns:
        str: IP адрес клиента
    """
    # X-Forwarded-For header (load balancer)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    # X-Real-IP header (nginx)
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    # Fallback to client IP
    return request.client.host if request.client else "unknown"
