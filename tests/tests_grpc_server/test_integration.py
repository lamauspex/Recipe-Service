import pytest
import asyncio

from backend.service_user.src.infrastructure.grpc.runner import GrpcRunner
from backend.service_recipe.src.infrastructure.grpc.client import (
    UserServiceClient)


class TestGrpcIntegration:
    """Интеграционные тесты gRPC (реальный сервер + клиент)"""

    @pytest.mark.asyncio
    async def test_full_grpc_cycle(self):
        """Полный цикл: сервер запущен → вызов → сервер остановлен"""
        # Setup
        runner = GrpcRunner(port=50052)  # Другой порт для теста
        client = UserServiceClient(
            host="localhost",
            port=50052
        )

        # Start server
        await runner.start()
        await asyncio.sleep(0.5)  # Дать время на запуск

        try:
            # Test connection
            await client.connect()
            result = await client.validate_token("test_token")

            # Should handle gracefully (even if token invalid)
            assert "valid" in result

        finally:
            # Cleanup
            await client.close()
            await runner.stop()
