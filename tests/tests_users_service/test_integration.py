"""
Интеграционные тесты логина - TestLoginEndpoint
Интеграционные тесты логаута - TestLogoutEndpoint
Интеграционные тесты обновления токенов - TestRefreshEndpoint
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

from backend.service_user.src.app_users import create_app


@pytest.fixture
def app():
    return create_app()


class TestLoginEndpoint:
    """Тесты эндпоинта логина"""

    @pytest.fixture
    def mock_auth_service(self):
        """Мок сервиса аутентификации"""
        from backend.service_user.src.schemas.auth.auth_dto import TokenPairDTO

        mock = AsyncMock()
        mock.authenticate_and_create_tokens.return_value = TokenPairDTO(
            access_token="access_token_here",
            refresh_token="refresh_token_here"
        )
        return mock

    @pytest.fixture
    def app(self, mock_auth_service):
        """Создание тестового приложения с моком"""
        app = create_app()

        from backend.service_user.src.infrastructure.dependencies import get_auth_service
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        return app

    @pytest.mark.asyncio
    async def test_login_missing_email_returns_422(self, app):
        """Логин без email должен возвращать 422"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "password": "SecurePass123!"
                }
            )

            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_password_returns_422(self, app):
        """Логин без пароля должен возвращать 422"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com"
                }
            )

            assert response.status_code == 422


class TestLogoutEndpoint:
    """Тесты эндпоинта логаута"""

    @pytest.fixture
    def mock_token_repository(self):
        """Мок репозитория токенов"""
        mock = AsyncMock()
        mock.revoke_token.return_value = None
        return mock

    @pytest.fixture
    def app(self, mock_token_repository):
        """Создание тестового приложения с моком"""
        app = create_app()

        from backend.service_user.src.infrastructure.dependencies import get_token_repository
        app.dependency_overrides[get_token_repository] = lambda: mock_token_repository

        return app

    @pytest.mark.asyncio
    async def test_logout_valid_token_returns_200(self, app):
        """Выход с валидным токеном должен возвращать 200"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/logout",
                json={
                    "refresh_token": "valid_token_to_revoke"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "message" in data

    @pytest.mark.asyncio
    async def test_logout_missing_token_returns_422(self, app):
        """Выход без токена должен возвращать 422"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/logout",
                json={}
            )

            assert response.status_code == 422


class TestRefreshEndpoint:
    """Тесты эндпоинта обновления токенов"""

    @pytest.fixture
    def mock_auth_service(self):
        """Мок сервиса аутентификации"""
        from backend.service_user.src.schemas.auth.auth_dto import TokenPairDTO

        mock = AsyncMock()
        mock.refresh_access_token.return_value = TokenPairDTO(
            access_token="new_access_token",
            refresh_token="new_refresh_token"
        )
        return mock

    @pytest.fixture
    def app(self, mock_auth_service):
        """Создание тестового приложения с моком"""
        app = create_app()

        from backend.service_user.src.infrastructure.dependencies import get_auth_service
        app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

        return app

    @pytest.mark.asyncio
    async def test_refresh_missing_token_returns_422(self, app):
        """Обновление без токена должно возвращать 422"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/v1/auth/refresh",
                json={}
            )

            assert response.status_code == 422
