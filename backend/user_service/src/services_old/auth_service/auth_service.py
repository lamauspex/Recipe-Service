"""
Главный сервис аутентификации
Обновлен для использования новых утилит и базового класса
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from backend.user_service.src.models import User
from backend.user_service.src.repository import UserRepository, RefreshTokenRepository
from backend.user_service.src.exceptions.base import (
    NotFoundException,
    ConflictException,
    UnauthorizedException
)
from auth_service.password_service import PasswordService
from auth_service.jwt_service import JWTService
from auth_service.refresh_token_service import RefreshTokenService
from common.base_service import BaseService
from common.response_builder import ResponseBuilder


class AuthService(BaseService):
    """Основной сервис аутентификации"""

    def __init__(
        self,
        db_session,
        jwt_service: JWTService,
        password_service: PasswordService,
        refresh_token_service: RefreshTokenService
    ):
        super().__init__()
        self.db = db_session
        self.user_repo = UserRepository(db_session)
        self.jwt_service = jwt_service
        self.password_service = password_service
        self.refresh_token_service = refresh_token_service

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Аутентификация пользователя"""
        try:
            # Ищем пользователя по email
            user = self.user_repo.get_user_by_email(email)
            if not user:
                return ResponseBuilder.error("Неверный email или пароль", error_code="INVALID_CREDENTIALS")

            # Проверяем, не заблокирован ли аккаунт
            if user.is_locked:
                return ResponseBuilder.error("Аккаунт заблокирован", error_code="ACCOUNT_LOCKED")

            # Проверяем пароль
            if not self.password_service.verify_password(password, user.hashed_password):
                return ResponseBuilder.error("Неверный email или пароль", error_code="INVALID_CREDENTIALS")

            # Проверяем, активен ли пользователь
            if not user.is_active:
                return ResponseBuilder.error("Аккаунт деактивирован", error_code="ACCOUNT_DEACTIVATED")

            # Генерируем токены
            user_data = {"sub": str(user.id), "email": user.email}
            access_token = self.jwt_service.create_access_token(user_data)
            refresh_token = self.jwt_service.create_refresh_token(user_data)

            # Сохраняем refresh токен
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
            self.refresh_token_service.create_refresh_token(
                user.id, refresh_token, expires_at)

            # Обновляем время входа
            user.last_login_at = datetime.now(timezone.utc)
            self.db.commit()

            return ResponseBuilder.success(
                "Аутентификация успешна",
                data={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "user": {
                        "id": str(user.id),
                        "email": user.email,
                        "full_name": user.full_name
                    }
                }
            )

        except Exception as e:
            self.db.rollback()
            return self._handle_error(e, "аутентификации пользователя")

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Обновление access токена"""
        try:
            # Проверяем refresh токен
            if not self.refresh_token_service.get_valid_token(refresh_token):
                return ResponseBuilder.error("Недействительный refresh токен", error_code="INVALID_REFRESH_TOKEN")

            # Декодируем токен для получения данных пользователя
            payload = self.jwt_service.decode_token(refresh_token)
            if not payload:
                return ResponseBuilder.error("Недействительный токен", error_code="INVALID_TOKEN")

            user_id = payload.get("sub")
            email = payload.get("email")

            if not user_id or not email:
                return ResponseBuilder.error("Недействительные данные в токене", error_code="INVALID_TOKEN_DATA")

            # Проверяем, существует ли пользователь
            user = self.user_repo.get_user_by_id(user_id)
            if not user or not user.is_active:
                return ResponseBuilder.error("Пользователь не найден или неактивен", error_code="USER_NOT_FOUND")

            # Генерируем новый access токен
            user_data = {"sub": user_id, "email": email}
            new_access_token = self.jwt_service.create_access_token(user_data)

            return ResponseBuilder.success(
                "Access токен обновлен",
                data={
                    "access_token": new_access_token,
                    "token_type": "bearer"
                }
            )

        except Exception as e:
            return self._handle_error(e, "обновления access токена")

    def logout(self, refresh_token: str) -> Dict[str, Any]:
        """Выход пользователя"""
        try:
            # Отзываем refresh токен
            result = self.refresh_token_service.revoke_token(refresh_token)

            if result.get("success"):
                return ResponseBuilder.success("Выход выполнен успешно")
            else:
                return ResponseBuilder.error("Ошибка при выходе", error_code="LOGOUT_ERROR")

        except Exception as e:
            return self._handle_error(e, "выхода пользователя")

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Проверка токена"""
        try:
            payload = self.jwt_service.decode_token(token)
            if not payload:
                return ResponseBuilder.error("Недействительный токен", error_code="INVALID_TOKEN")

            user_id = payload.get("sub")
            if not user_id:
                return ResponseBuilder.error("Недействительные данные в токене", error_code="INVALID_TOKEN_DATA")

            user = self.user_repo.get_user_by_id(user_id)
            if not user or not user.is_active:
                return ResponseBuilder.error("Пользователь не найден или неактивен", error_code="USER_NOT_FOUND")

            return ResponseBuilder.success(
                "Токен валиден",
                data={
                    "user": {
                        "id": str(user.id),
                        "email": user.email,
                        "full_name": user.full_name
                    }
                }
            )

        except Exception as e:
            return self._handle_error(e, "проверки токена")
