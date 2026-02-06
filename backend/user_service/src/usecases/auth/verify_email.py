"""
Usecase для подтверждения email
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from ...schemas.requests import BaseRequestDTO
from ...schemas.responses import BaseResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import NotFoundException, ValidationException


class VerifyEmailUsecase(BaseUsecase):
    """Usecase для подтверждения email"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: BaseRequestDTO) -> BaseResponseDTO:
        """Выполнение подтверждения email"""
        try:
            # Получение токена верификации
            verification_token = getattr(request, 'token', None)
            if not verification_token:
                raise ValidationException("Verification token is required")

            # Проверка токена
            user_id = await self._verify_email_token(verification_token)
            if not user_id:
                raise ValidationException(
                    "Invalid or expired verification token")

            # Получение пользователя
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                raise NotFoundException("User not found")

            # Проверка, что email еще не подтвержден
            if user.email_verified:
                return BaseResponseDTO(
                    success=True,
                    message="Email is already verified"
                )

            # Подтверждение email
            update_data = {
                "email_verified": True,
                "updated_at": datetime.utcnow().isoformat()
            }

            updated_user = await self.user_repository.update(user_id, update_data)
            if not updated_user:
                raise ValidationException("Failed to verify email")

            # Аннулирование токена
            await self._invalidate_verification_token(verification_token)

            # Возврат результата
            return BaseResponseDTO(
                success=True,
                message="Email verified successfully"
            )

        except Exception as e:
            if isinstance(e, (NotFoundException, ValidationException)):
                raise e
            raise ValidationException(f"Failed to verify email: {str(e)}")

    async def _verify_email_token(self, token: str) -> Optional[str]:
        """Проверка токена верификации email"""
        try:
            # Заглушка - в реальной реализации здесь был бы поиск токена в БД
            # и возврат ID пользователя

            # Проверка формата токена
            if not token or len(token) < 20:
                return None

            # Симуляция успешной проверки токена
            # В реальной реализации здесь был бы код для:
            # 1. Поиска токена в таблице verification_tokens
            # 2. Проверки срока действия токена
            # 3. Возврата user_id

            # Для демонстрации возвращаем заглушку
            return "user_id_from_verification_token"

        except Exception:
            return None

    async def _invalidate_verification_token(self, token: str) -> bool:
        """Аннулирование токена верификации"""
        # Заглушка - в реальной реализации здесь был бы запрос к БД
        print(f"Invalidating verification token: {token}")
        return True


class ResendVerificationUsecase(BaseUsecase):
    """Usecase для повторной отправки подтверждения email"""

    def __init__(self, user_repository, **kwargs):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def execute(self, request: BaseRequestDTO) -> BaseResponseDTO:
        """Выполнение повторной отправки подтверждения"""
        try:
            # Получение email из запроса
            email = getattr(request, 'email', None)
            if not email:
                raise ValidationException("Email is required")

            # Поиск пользователя
            user = await self.user_repository.get_by_email(email)

            # Для безопасности не сообщаем, существует ли пользователь
            if not user or user.email_verified:
                return BaseResponseDTO(
                    success=True,
                    message="If the email exists and is not verified, a verification email has been sent"
                )

            # Проверка лимита отправки (заглушка)
            can_send = await self._check_resend_limit(user.id)
            if not can_send:
                raise ValidationException(
                    "Too many verification emails sent. Please try again later.")

            # Генерация нового токена
            verification_token = await self._generate_verification_token(user.id)

            # Сохранение токена (заглушка)
            await self._store_verification_token(user.id, verification_token)

            # Отправка email (заглушка)
            await self._send_verification_email(email, verification_token)

            # Обновление времени последней отправки (заглушка)
            await self._update_last_resend_time(user.id)

            # Возврат результата
            return BaseResponseDTO(
                success=True,
                message="If the email exists and is not verified, a verification email has been sent"
            )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise e
            raise ValidationException(
                f"Failed to resend verification email: {str(e)}")

    async def _generate_verification_token(self, user_id: str) -> str:
        """Генерация токена верификации"""
        import secrets
        import string

        # Генерация случайного токена
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))

        # Добавление временной метки
        timestamp = int(datetime.utcnow().timestamp())
        return f"verify_{token}.{timestamp}"

    async def _store_verification_token(self, user_id: str, token: str) -> bool:
        """Сохранение токена верификации (заглушка)"""
        # Заглушка - в реальной реализации здесь был бы запрос к БД
        print(f"Storing verification token for user {user_id}: {token}")
        return True

    async def _send_verification_email(self, email: str, token: str) -> bool:
        """Отправка email с токеном (заглушка)"""
        # Заглушка - в реальной реализации здесь была бы отправка email
        verification_link = f"https://example.com/verify-email?token={token}"
        print(
            f"Sending verification email to {email} with link: {verification_link}")
        return True

    async def _check_resend_limit(self, user_id: str) -> bool:
        """Проверка лимита повторной отправки"""
        # Заглушка - в реальной реализации здесь был бы запрос к БД
        # для проверки времени последней отправки
        return True

    async def _update_last_resend_time(self, user_id: str) -> bool:
        """Обновление времени последней отправки (заглушка)"""
        # Заглушка - в реальной реализации здесь был бы запрос к БД
        return True
