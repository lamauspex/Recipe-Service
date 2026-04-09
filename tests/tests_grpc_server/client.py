import grpc

from backend.shared import user_service_pb2
from backend.shared import user_service_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_service_pb2_grpc.UserServiceStub(channel)

        # Тест метода ValidateToken
        print("Testing ValidateToken...")
        response = stub.ValidateToken(
            user_service_pb2.ValidateTokenRequest(token="valid_token")
        )
        print(f"ValidateToken response: {response}")

        # Тест метода GetUserById
        print("\nTesting GetUserById...")
        response = stub.GetUserById(
            user_service_pb2.GetUserByIdRequest(user_id="123")
        )
        print(f"GetUserById response: {response}")


if __name__ == '__main__':
    run()
