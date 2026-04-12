"""
Сервис запуска User Service
"""

import uvicorn

from backend.service_user.src.app_users import create_app
from backend.service_user.src.infrastructure.container import container
from backend.service_user.src.infrastructure.grpc.runner import GrpcRunner


class ServiceRunner:
    """Управление запуском сервиса"""

    def __init__(self):
        self.grpc_runner = None

    def run(self):
        """Запуск сервиса"""
        config = container.api_config()
        grpc_config = container.grpc_config()

        app = create_app()

        if grpc_config and grpc_config.ENABLE_GRPC:
            self.grpc_runner = GrpcRunner(port=grpc_config.GRPC_PORT)
            self.grpc_runner.run_in_background()

        try:
            uvicorn.run(
                app=app,
                host=config.HOST,
                port=config.PORT,
                log_level="info" if config.DEBUG else "warning",
                access_log=config.DEBUG
            )
        finally:
            self._shutdown()

    def _shutdown(self):
        if self.grpc_runner:
            print(">>> Останавливаем gRPC сервер...")
            self.grpc_runner.stop()
