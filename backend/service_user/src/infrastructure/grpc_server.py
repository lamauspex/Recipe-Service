""" gRPC сервер для user_service """

import grpc
from uuid import UUID
from concurrent import futures

from backend.service_user.src.repositories.sql_user_repository import (
    SQLUserRepository)
from backend.shared.proto import user_service_pb2, user_service_pb2_grpc
from backend.service_user.src.infrastructure.container import container


class UserServiceServicer(user_service_pb2_grpc.UserServiceServicer):
    """Реализация gRPC сервиса UserService"""

    def __init__(self):
        self.jwt_service = container.jwt_service()

    def ValidateToken(self, request, context):
        """Валидация JWT токена"""
        token = request.token

        if not token:
            return user_service_pb2.ValidateTokenResponse(
                valid=False,
                error="Token is required"
            )

        payload = self.jwt_service.decode_token(token)

        if not payload:
            return user_service_pb2.ValidateTokenResponse(
                valid=False,
                error="Invalid or expired token"
            )

        return user_service_pb2.ValidateTokenResponse(
            valid=True,
            user_id=payload.get("sub") or payload.get("user_id"),
            email=payload.get("email", "")
        )

    def GetUserById(self, request, context):
        """Получение пользователя по ID"""

        # Создаём сессию БД
        session_manager = container.session_manager()
        session = session_manager.SessionLocal()

        try:
            user_repo = SQLUserRepository(session)

            # Получаем user_id из запроса (строка -> UUID)
            user_id = UUID(request.user_id)
            user = user_repo.get_user_by_id(user_id)

            if not user:
                return user_service_pb2.GetUserByIdResponse(
                    id=request.user_id,
                    email="",
                    user_name="",
                    exists=False
                )

            return user_service_pb2.GetUserByIdResponse(
                id=str(user.id),
                email=user.email,
                user_name=user.user_name,
                is_active=user.is_active,
                exists=True
            )
        finally:
            session.close()


def serve_grpc(port=50051):
    """Запуск gRPC сервера"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(
        UserServiceServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    return server
