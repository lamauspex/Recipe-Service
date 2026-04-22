"""
Реализация gRPC сервиса UserService
"""


import grpc
from uuid import UUID

from grpc_health.v1 import health_pb2
from google.rpc import status_pb2


from backend.service_user.src.infrastructure.container import container
from backend.shared.logging.logger import get_logger
from backend.shared.proto import user_service_pb2, user_service_pb2_grpc


logger = get_logger(__name__).bind(
    layer="grpc",
    service="user"
)


class UserServiceServicer(user_service_pb2_grpc.UserServiceServicer):
    """Реализация gRPC сервиса UserService"""

    def __init__(self):
        self.jwt_service = container.jwt_service()

    def CheckHealth(self, request, context):
        """Проверка здоровья gRPC сервера"""
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING
        )

    def ValidateToken(self, request, context):
        """Валидация JWT токена"""
        token = request.token

        if not token:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Token is required")
            return user_service_pb2.ValidateTokenResponse(
                valid=False,
                user_id="",
                email="",
                error=status_pb2.Status(
                    code=grpc.StatusCode.INVALID_ARGUMENT.value[0],
                    message="Token is required"
                )
            )

        try:
            payload = self.jwt_service.decode_token(token)
        except Exception as e:
            logger.error(f"JWT decode error: {e}")
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid token format")
            return user_service_pb2.ValidateTokenResponse(
                valid=False,
                user_id="",
                email="",
                error=status_pb2.Status(
                    code=grpc.StatusCode.UNAUTHENTICATED.value[0],
                    message="Invalid token format"
                )
            )

        if not payload:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            context.set_details("Invalid or expired token")
            return user_service_pb2.ValidateTokenResponse(
                valid=False,
                user_id="",
                email="",
                error=status_pb2.Status(
                    code=grpc.StatusCode.UNAUTHENTICATED.value[0],
                    message="Invalid or expired token"
                )
            )

        user_id = payload.get("sub") or payload.get("user_id") or ""
        email = payload.get("email") or ""

        return user_service_pb2.ValidateTokenResponse(
            valid=True,
            user_id=user_id,
            email=email,
            error=status_pb2.Status()
        )

    def GetUserById(self, request, context):
        """Получение пользователя по ID"""
        session_manager = container.session_manager()
        user_repo_class = container.sql_user_repository()

        with session_manager.SessionLocal() as session:
            user_repo = user_repo_class(session)
            try:
                try:
                    user_id = UUID(request.user_id)
                except ValueError:
                    context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                    context.set_details("Invalid user ID format")
                    return user_service_pb2.GetUserByIdResponse(
                        id="",
                        email="",
                        user_name="",
                        is_active=False,
                        exists=False
                    )

                user = user_repo.get_user_by_id(user_id)

                if not user:
                    return user_service_pb2.GetUserByIdResponse(
                        id="",
                        email="",
                        user_name="",
                        is_active=False,
                        exists=False
                    )

                return user_service_pb2.GetUserByIdResponse(
                    id=str(user.id),
                    email=user.email,
                    user_name=user.user_name,
                    is_active=user.is_active,
                    exists=True
                )
            except Exception as e:
                logger.error(f"Error getting user by ID: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Internal server error")
                return user_service_pb2.GetUserByIdResponse(
                    id="",
                    email="",
                    user_name="",
                    is_active=False,
                    exists=False
                )
