import grpc
from concurrent import futures
import user_service_pb2
import user_service_pb2_grpc


class UserService(user_service_pb2_grpc.UserServiceServicer):
    def ValidateToken(self, request, context):
        # Здесь — ваша реальная логика валидации токена
        if request.token == "valid_token":
            return user_service_pb2.ValidateTokenResponse(
                valid=True,
                user_id="123",
                email="user@example.com",
                error=""
            )
        else:
            return user_service_pb2.ValidateTokenResponse(
                valid=False,
                user_id="",
                email="",
                error="Invalid token"
            )

    def GetUserById(self, request, context):
        # Здесь — ваша логика получения пользователя
        return user_service_pb2.GetUserByIdResponse(
            id=request.user_id,
            email="user@example.com",
            user_name="John Doe",
            is_active=True,
            exists=True
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(), server)
    server.add_insecure_port('[::]:50051')
    print("gRPC Server started on port 50051")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
