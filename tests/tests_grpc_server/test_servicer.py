from dotenv import load_dotenv
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from backend.shared.proto import user_service_pb2
from backend.service_user.src.infrastructure.grpc.server import UserServiceServicer


# Загрузить .env.test перед импортом container
TESTS_DIR = Path(__file__).parent.parent
if (TESTS_DIR / ".env.test").exists():
    os.environ["ENV_FILE"] = str(TESTS_DIR / ".env.test")

# Загрузить переменные окружения
load_dotenv(TESTS_DIR / ".env.test")


class TestUserServiceServicer:
    """Тесты gRPC Servicer для User Service"""

    @pytest.fixture
    def context(self):
        return MagicMock()

    def test_validate_token_success(self, context):
        """Валидация успешного токена"""
        with patch('backend.service_user.src.infrastructure.grpc.server.container') as mock_container:
            mock_jwt = MagicMock()
            mock_jwt.decode_token = MagicMock(return_value={
                "sub": "123",
                "email": "test@example.com"
            })
            mock_container.jwt_service.return_value = mock_jwt

            servicer = UserServiceServicer()
            request = user_service_pb2.ValidateTokenRequest(token="valid_jwt")

            response = servicer.ValidateToken(request, context)

            assert response.valid is True
            assert response.user_id == "123"
            assert response.email == "test@example.com"

    def test_validate_token_invalid(self, context):
        """Валидация невалидного токена"""
        with patch('backend.service_user.src.infrastructure.grpc.server.container') as mock_container:
            mock_jwt = MagicMock()
            mock_jwt.decode_token = MagicMock(return_value=None)
            mock_container.jwt_service.return_value = mock_jwt

            servicer = UserServiceServicer()
            request = user_service_pb2.ValidateTokenRequest(
                token="invalid_jwt")

            response = servicer.ValidateToken(request, context)

            assert response.valid is False
            assert response.user_id == ""
            assert response.email == ""

    def test_get_user_by_id_exists(self, context):
        """Получение существующего пользователя"""
        mock_user = MagicMock()
        mock_user.id = "123"
        mock_user.email = "test@example.com"
        mock_user.user_name = "Test User"
        mock_user.is_active = True

        mock_session_manager = MagicMock()
        mock_session_manager.SessionLocal = MagicMock()
        mock_session_manager.SessionLocal.__enter__ = MagicMock(
            return_value=MagicMock())
        mock_session_manager.SessionLocal.__exit__ = MagicMock(
            return_value=False)

        mock_repo_instance = MagicMock()
        mock_repo_instance.get_user_by_id = MagicMock(return_value=mock_user)

        with patch('backend.service_user.src.infrastructure.container.container') as mock_container:
            mock_container.session_manager.return_value = mock_session_manager
            mock_container.sql_user_repository.return_value = MagicMock(
                return_value=mock_repo_instance)

            servicer = UserServiceServicer()
            request = user_service_pb2.GetUserByIdRequest(user_id="123")

            response = servicer.GetUserById(request, context)

            assert response.exists is True
            assert response.id == "123"
            assert response.email == "test@example.com"
            assert response.user_name == "Test User"
            assert response.is_active is True

    def test_get_user_by_id_not_found(self, context):
        """Получение несуществующего пользователя"""
        mock_session_manager = MagicMock()
        mock_session_manager.SessionLocal = MagicMock()
        mock_session_manager.SessionLocal.__enter__ = MagicMock(
            return_value=MagicMock())
        mock_session_manager.SessionLocal.__exit__ = MagicMock(
            return_value=False)

        with patch('backend.service_user.src.infrastructure.grpc.server.container') as mock_container:
            mock_container.session_manager.return_value = mock_session_manager

            servicer = UserServiceServicer()
            request = user_service_pb2.GetUserByIdRequest(user_id="999")

            response = servicer.GetUserById(request, context)

            assert response.exists is False
            assert response.id == ""
            assert response.email == ""
            assert response.user_name == ""
            assert response.is_active is False
