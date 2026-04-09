"""
Запуск gRPC сервера в отдельном процессе
Изолирован от FastAPI/uvicorn для надёжности
"""


import signal
import sys
import logging
import grpc
from concurrent import futures

from backend.service_user.src.infrastructure.grpc_server import (
    UserServiceServicer)
from backend.shared.proto import user_service_pb2_grpc

logger = logging.getLogger(__name__)


# Глобальная ссылка на сервер для graceful shutdown
_grpc_server = None


def signal_handler(signum, frame):
    """Обработчик сигналов для чистого завершения"""
    print(f">>> [grpc_process] Received signal {signum}, shutting down...")
    if _grpc_server:
        _grpc_server.stop(grace=5)
    sys.exit(0)


def main(port: int = 50051):
    """Точка входа для запуска gRPC сервера"""
    global _grpc_server

    print(f">>> [grpc_process] Starting gRPC server on port {port}...")

    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Создаём и запускаем сервер напрямую
        print(">>> [grpc_process] Creating server...")
        _grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        user_service_pb2_grpc.add_UserServiceServicer_to_server(
            UserServiceServicer(), _grpc_server
        )
        _grpc_server.add_insecure_port(f'[::]:{port}')

        print(">>> [grpc_process] Starting server...")
        _grpc_server.start()

        print(f">>> [grpc_process] gRPC server started on port {port}")
        print(f">>> [grpc_process] PID: {__import__('os').getpid()}")

        # Ожидаем завершения
        _grpc_server.wait_for_termination()

    except Exception as e:
        print(f">>> [grpc_process] ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print(">>> [grpc_process] Shutdown complete")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50051
    main(port)
