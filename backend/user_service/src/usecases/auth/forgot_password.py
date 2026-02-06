"""
Usecase для восстановления пароля
"""

from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from ...schemas.requests import PasswordResetRequestDTO, PasswordResetConfirmRequestDTO
from ...schemas.responses import PasswordResetResponseDTO, BaseResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException
from ...infrastructure.common.password_utility import password_utility


class ForgotPasswordUsecase(BaseUsecase):
    """Usecase для восстановления пароля"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: PasswordResetRequestDTO
    ) -> PasswordResetResponseDTO:
        """Выполнение восстановления пароля"""
        try:
            # Валидация email
            if not request.email:
                raise ValidationException("Email is required")

            # Поиск пользователя
            user = await self.user_repository.get_by_email(request.email)

            # Для безопасности не сообщаем, существует ли пользователь
            if not user:
                return PasswordResetResponseDTO(
                    success=True,
                    message="If the email exists, a reset link has been sent"
                )

            # Генерация токена сброса пароля
            reset_token = await self._generate_reset_token(user.id)

            # Сохранение токена (заглушка)
            await self._store_reset_token(user.id, reset_token)

            # Отправка email с токеном (заглушка)
            await self._send_reset_email(request.email, reset_token)

            # Возврат результата
            return PasswordResetResponseDTO(
                success=True,
                message="If the email exists, a reset link has been sent"
            )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise e
            raise ValidationException(
                f"Failed to process password reset request: {str(e)}")

    async def _generate_reset_token(self, user_id: str) -> str:
        """Генерация токена сброса пароля"""
        import secrets
        import string

        # Генерация случайного токена
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))

        # Добавление временной метки
        timestamp = int(datetime.utcnow().timestamp())
        return f"{token}.{timestamp}"

    async def _store_reset_token(self, user_id: str, token: str) -> bool:
        """Сохранение токена сброса (заглушка)"""
        # Заглушка - в реальной реализации здесь был бы запрос к БД
        # для сохранения токена с временем истечения
        print(f"Reset token for user {user_id}: {token}")
        return True

    async def _send_reset_email(self, email: str, token: str) -> bool:
        """Отправка email с токеном (заглушка)"""
        # Заглушка - в реальной реализации здесь была бы отправка email
        reset_link = f"https://example.com/reset-password?token={token}"
        print(f"Sending reset email to {email} with link: {reset_link}")
        return True


class ResetPasswordUsecase(BaseUsecase):
    """Usecase для сброса пароля"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(
        self,
        request: PasswordResetConfirmRequestDTO
    ) -> BaseResponseDTO:
        """Выполнение сброса пароля"""
        try:
            # Валидация токена
            if not request.token or not request.new_password:
                raise ValidationException(
                    "Token and new password are required")

            # Проверка токена
            user_id = await self._verify_reset_token(request.token)
            if not user_id:
                raise ValidationException("Invalid or expired reset token")

            # Получение пользователя
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")

            # Валидация сложности нового пароля
            # Заглушка - в реальной реализации использовался бы SecurityService
            if len(request.new_password) < 8:
                raise ValidationException(
                    "Password must be at least 8 characters long")

            # Хеширование нового пароля
            new_hashed_password = password_utility.hash_password(
                request.new_password)

            # Обновление пароля
            update_data = {
                "hashed_password": new_hashed_password,
                "updated_at": datetime.utcnow().isoformat()
            }

            updated_user = await self.user_repository.update(user_id, update_data)
            if not updated_user:
                raise ValidationException("Failed to reset password")

            # Аннулирование токена
            await self._invalidate_reset_token(request.token)

            # Возврат результата
            return BaseResponseDTO(
                success=True,
                message="Password reset successfully"
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to reset password: {str(e)}")

    async def _verify_reset_token(self, token: str) -> Optional[str]:
        """Проверка токена сброса пароля"""
        try:
            # Парсинг токена
            parts = token.split('.')
            if len(parts) != 2:
                return None

            token_value, timestamp_str = parts
            timestamp = int(timestamp_str)

            # Проверка срока действия (24 часа)
            token_age = datetime.utcnow().timestamp() - timestamp
            if token_age > 24 * 3600:  # 24 часа
                return None

            # Заглушка - в реальной реализации здесь был бы поиск токена в БД
            # и возврат ID пользователя
            return "user_id_from_token"

        except Exception:
            return None

    async def _invalidate_reset_token(self, token: str) -> bool:
        """Аннулирование токена"""
        # Заглушка - в реальной реализации здесь был бы запрос к БД
        print(f"Invalidating reset token: {token}")
        return True
