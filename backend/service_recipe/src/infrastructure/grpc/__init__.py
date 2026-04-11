"""
gRPC client module for Recipe Service

Экспортирует:
- UserServiceClient: gRPC клиент для взаимодействия с user_service
"""

from backend.service_recipe.src.infrastructure.grpc.client import (
    UserServiceClient
)

__all__ = [
    "UserServiceClient"
]
