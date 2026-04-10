"""
gRPC модуль для User Service

Содержит:
- Сервер для обработки gRPC запросов
- Клиент для вызова других сервисов
- Управление жизненным циклом gRPC
"""

from .server import UserServiceServicer
from .runner import GrpcRunner

__all__ = [
    "UserServiceServicer",
    "GrpcRunner",
]
