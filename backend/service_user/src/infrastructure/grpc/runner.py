"""
Управление запуском gRPC сервера

Поддерживает:
- Запуск в отдельном потоке (вместе с FastAPI)
- Запуск как отдельный процесс (--grpc-only)
- Graceful shutdown
"""


import sys
import socket
from typing import Optional

import argparse
import grpc
from concurrent import futures
from grpc_health.v1 import health_pb2_grpc

from backend.shared.logging.logger import get_logger
from backend.shared.proto import user_service_pb2_grpc
from backend.service_user.src.infrastructure.grpc.server import (
    UserServiceServicer)


logger = get_logger(__name__).bind(
    layer="grpc",
    service="user"
)


class GrpcRunner:
    """Управление gRPC сервером"""

    def __init__(self, port: int = 50051):
        self.port = port
        self._server: Optional[grpc.Server] = None
        self._running = False

    def run(self):
        """Запуск gRPC сервера (блокирующий)"""
        logger.info(f"Starting gRPC server on port {self.port}")

        # Проверка доступности порта
        if not self._is_port_available(self.port):
            raise RuntimeError(f"Port {self.port} is already in use")

        # Создаём сервер
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        # Добавляем сервис пользователя
        user_service_pb2_grpc.add_UserServiceServicer_to_server(
            UserServiceServicer(), self._server
        )

        # Добавляем health check
        health_pb2_grpc.add_HealthServicer_to_server(
            health_pb2_grpc.HealthServicer(), self._server
        )

        self._server.add_insecure_port(f'[::]:{self.port}')

        # Запускаем
        self._server.start()
        self._running = True
        logger.info(f"gRPC server running on port {self.port}")

        # Ожидаем
        self._server.wait_for_termination()

    def run_sync(self):
        """Запуск в синхронном режиме (для потока)"""
        self.run()

    def run_in_background(self):
        """Запуск gRPC в фоновом потоке"""
        import threading
        thread = threading.Thread(target=self.run_sync, daemon=True)
        thread.start()
        logger.info(f"gRPC server started in background on port {self.port}")

    def stop(self, grace: int = 5):
        """Остановка сервера"""
        if self._server and self._running:
            logger.info("Stopping gRPC server...")
            self._server.stop(grace)
            self._running = False
            logger.info("gRPC server stopped")

    def _signal_handler(self, signum, frame):
        """Обработчик сигналов"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop(grace=5)
        sys.exit(0)

    @staticmethod
    def _is_port_available(port: int) -> bool:
        """Проверка доступности порта"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return True
            except OSError:
                return False


def main():
    """Точка входа для запуска как отдельного процесса"""
    parser = argparse.ArgumentParser(description="gRPC Server Runner")
    parser.add_argument(
        "--port", type=int, default=50051,
        help="Port to listen on"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Запуск
    runner = GrpcRunner(port=args.port)
    runner.run()


if __name__ == "__main__":
    main()
