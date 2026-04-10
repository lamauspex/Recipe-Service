from pydantic import Field

from .base import BaseConfig


class GrpcConfig(BaseConfig):
    """Конфигурация gRPC сервера"""

    ENABLE_GRPC: bool = Field(
        default=True,
        description="Включить gRPC сервер"
    )
    GRPC_PORT: int = Field(
        default=50051,
        description="Порт для gRPC сервера"
    )
