""" gRPC клиент для recipe_service """

import grpc
from typing import Optional

from backend.shared.proto import (
    user_service_pb2
)
from backend.shared.proto import user_service_pb2_grpc


class UserServiceClient:
    """ Клиент для взаимодействия с user_service через gRPC """

    def __init__(self,
                 host: str = "localhost",
                 port: int = 50051):
        self.host = host
        self.port = port
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[user_service_pb2_grpc.UserServiceStub] = None

    async def connect(self):
        """Установка соединения"""
        self._channel = grpc.aio.insecure_channel(f'{self.host}:{self.port}')
        self._stub = user_service_pb2_grpc.UserServiceStub(self._channel)

    async def close(self):
        """Закрытие соединения"""
        if self._channel:
            await self._channel.close()

    async def validate_token(self, token: str) -> dict:
        """Валидация токена через gRPC"""
        if not self._stub:
            await self.connect()

        try:
            response = await self._stub.ValidateToken(
                user_service_pb2.ValidateTokenRequest(token=token)
            )
            return {
                "valid": response.valid,
                "user_id": response.user_id,
                "email": response.email,
                "error": response.error
            }
        except grpc.RpcError as e:
            return {
                "valid": False,
                "error": f"gRPC error: {e.code()}"
            }

    async def get_user_by_id(self, user_id: str) -> dict:
        """Получение пользователя по ID"""
        if not self._stub:
            await self.connect()

        try:
            response = await self._stub.GetUserById(
                user_service_pb2.GetUserByIdRequest(user_id=user_id)
            )
            return {
                "id": response.id,
                "email": response.email,
                "user_name": response.user_name,
                "exists": response.exists
            }
        except grpc.RpcError as e:
            return {"exists": False, "error": str(e)}
