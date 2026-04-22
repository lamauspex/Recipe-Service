"""
Точка входа для gRPC сервера User Service
"""

from backend.service_user.src.infrastructure.grpc.runner import GrpcRunner

if __name__ == "__main__":
    runner = GrpcRunner()
    runner.run()
