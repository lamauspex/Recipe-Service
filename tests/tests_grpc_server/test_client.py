import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.service_recipe.src.infrastructure.grpc.client import (
    UserServiceClient)


class TestUserServiceClient:
    """Тесты gRPC Клиента для Recipe Service"""

    @pytest.fixture
    def client(self):
        return UserServiceClient(host="localhost", port=50051)

    @pytest.mark.asyncio
    async def test_connect_sets_up_channel(self, client):
        """Подключение создаёт channel и stub"""
        with patch('grpc.aio.insecure_channel') as mock_channel:
            await client.connect()

            mock_channel.assert_called_once_with("localhost:50051")
            assert client._channel is not None
            assert client._stub is not None

    @pytest.mark.asyncio
    async def test_close_closes_channel(self, client):
        """Закрытие закрывает channel"""
        with patch('grpc.aio.insecure_channel') as mock_channel:
            await client.connect()
            mock_channel_instance = client._channel

            await client.close()

            mock_channel_instance.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_token_returns_correct_format(self, client):
        """validate_token возвращает правильный формат"""
        with patch.object(client, '_stub') as mock_stub:
            mock_response = MagicMock()
            mock_response.valid = True
            mock_response.user_id = "123"
            mock_response.email = "test@example.com"
            mock_response.error = ""

            mock_stub.ValidateToken = AsyncMock(return_value=mock_response)

            result = await client.validate_token("test_token")

            assert result == {
                "valid": True,
                "user_id": "123",
                "email": "test@example.com",
                "error": ""
            }

    @pytest.mark.asyncio
    async def test_validate_token_handles_grpc_error(self, client):
        """validate_token обрабатывает gRPC ошибки"""
        with patch.object(client, '_stub') as mock_stub:
            from grpc import RpcError, StatusCode

            mock_stub.ValidateToken = AsyncMock(side_effect=RpcError())

            result = await client.validate_token("test_token")

            assert result["valid"] is False
            assert "gRPC error" in result["error"]
