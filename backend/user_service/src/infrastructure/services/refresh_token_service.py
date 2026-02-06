"""
Расширенный сервис для управления refresh токенами
Мигрирован из старой архитектуры с улучшениями и async поддержкой
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from uuid import UUID

from ...interfaces.token import TokenRepositoryInterface
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)


class RefreshTokenService:
    """Расширенный сервис для управления refresh токенами"""

    def __init__(
        self,
        token_repository: TokenRepositoryInterface,
        config: Optional[Dict[str, Any]] = None
    ):
        self.token_repository = token_repository
        self.config = config or {}

        # Конфигурация
        self.refresh_token_ttl_hours = self.config.get(
            'REFRESH_TOKEN_TTL_HOURS', 168)  # 7 дней
        self.max_tokens_per_user = self.config.get('MAX_TOKENS_PER_USER', 5)
        self.cleanup_interval_hours = self.config.get(
            'CLEANUP_INTERVAL_HOURS', 24)

    async def create_refresh_token(
        self,
        user_id: UUID,
        token: str,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Создание refresh токена
        Мигрировано из старого RefreshTokenService
        """
        try:
            if not token:
                raise ValidationException(
                    "Токен является обязательным параметром")

            # Расчет времени истечения токена
            if expires_at is None:
                expires_at = datetime.utcnow() + timedelta(hours=self.refresh_token_ttl_hours)

            # Проверяем лимит токенов для пользователя
            user_tokens = await self.token_repository.get_by_user_id(str(user_id))
            active_tokens = [t for t in user_tokens if t.get(
                'expires_at') and t['expires_at'] > datetime.utcnow()]

            if len(active_tokens) >= self.max_tokens_per_user:
                # Удаляем самый старый токен
                oldest_token = min(
                    active_tokens, key=lambda x: x['expires_at'])
                await self.revoke_token(oldest_token['token'])

            # Создание записи токена
            token_data = {
                "user_id": str(user_id),
                "token": token,
                "token_type": "refresh",
                "expires_at": expires_at,
                "created_at": datetime.utcnow(),
                "is_revoked": False
            }

            result = await self.token_repository.create(token_data)

            return {
                "success": True,
                "message": "Refresh токен успешно создан",
                "data": {
                    "token_id": result["id"],
                    "user_id": str(user_id),
                    "expires_at": expires_at.isoformat(),
                    "ttl_hours": self.refresh_token_ttl_hours
                }
            }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "VALIDATION_ERROR"
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при создании refresh токена: {str(e)}")

    async def revoke_token(self, token: str) -> Dict[str, Any]:
        """
        Отзыв токена
        Мигрировано из старого RefreshTokenService
        """
        try:
            if not token:
                raise ValidationException(
                    "Токен является обязательным параметром")

            # Поиск токена
            token_record = await self.token_repository.get_by_token(token)
            if not token_record:
                return {
                    "success": False,
                    "error": "Токен не найден",
                    "error_code": "TOKEN_NOT_FOUND"
                }

            # Проверяем, не отозван ли уже токен
            if token_record.get("is_revoked", False):
                return {
                    "success": True,
                    "message": "Токен уже отозван",
                    "data": {
                        "token": token,
                        "revoked_at": datetime.utcnow().isoformat()
                    }
                }

            # Отзываем токен
            success = await self.token_repository.revoke_token(token)

            if success:
                return {
                    "success": True,
                    "message": "Токен успешно отозван",
                    "data": {
                        "token": token,
                        "revoked_at": datetime.utcnow().isoformat()
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Не удалось отозвать токен",
                    "error_code": "REVOKE_FAILED"
                }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "VALIDATION_ERROR"
            }
        except Exception as e:
            raise DatabaseException(f"Ошибка при отзыве токена: {str(e)}")

    async def get_valid_token(self, token: str) -> Dict[str, Any]:
        """
        Получение валидного токена
        Мигрировано из старого RefreshTokenService
        """
        try:
            if not token:
                raise ValidationException(
                    "Токен является обязательным параметром")

            # Получение токена из репозитория
            token_record = await self.token_repository.get_valid_token(token)

            if not token_record:
                return {
                    "success": False,
                    "error": "Токен не найден или недействителен",
                    "error_code": "INVALID_TOKEN"
                }

            # Проверяем, что токен не отозван
            if token_record.get("is_revoked", False):
                return {
                    "success": False,
                    "error": "Токен отозван",
                    "error_code": "TOKEN_REVOKED"
                }

            # Проверяем, что токен не истек
            expires_at = token_record.get("expires_at")
            if expires_at and datetime.utcnow() > expires_at:
                return {
                    "success": False,
                    "error": "Токен истек",
                    "error_code": "TOKEN_EXPIRED"
                }

            return {
                "success": True,
                "message": "Токен валиден",
                "data": {
                    "token_id": token_record.get("id"),
                    "user_id": token_record.get("user_id"),
                    "token_type": token_record.get("token_type"),
                    "created_at": token_record.get("created_at").isoformat() if token_record.get("created_at") else None,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "is_revoked": token_record.get("is_revoked", False)
                }
            }

        except ValidationException as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "VALIDATION_ERROR"
            }
        except Exception as e:
            raise DatabaseException(f"Ошибка при проверке токена: {str(e)}")

    async def cleanup_expired_tokens(self) -> Dict[str, Any]:
        """
        Очистка истекших токенов
        Мигрировано из старого RefreshTokenService с расширенной функциональностью
        """
        try:
            # Выполняем очистку в репозитории
            cleaned_count = await self.token_repository.cleanup_expired_tokens()

            # Дополнительная очистка: удаляем старые отозванные токены
            revoked_cleanup_count = await self._cleanup_old_revoked_tokens()

            # Очистка неиспользуемых токенов (старше 30 дней)
            unused_cleanup_count = await self._cleanup_unused_tokens()

            total_cleaned = cleaned_count + revoked_cleanup_count + unused_cleanup_count

            return {
                "success": True,
                "message": f"Очистка токенов завершена. Удалено {total_cleaned} токенов",
                "data": {
                    "expired_tokens": cleaned_count,
                    "revoked_tokens": revoked_cleanup_count,
                    "unused_tokens": unused_cleanup_count,
                    "total_cleaned": total_cleaned,
                    "cleanup_timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            raise DatabaseException(f"Ошибка при очистке токенов: {str(e)}")

    async def revoke_all_user_tokens(self, user_id: UUID) -> Dict[str, Any]:
        """
        Отзыв всех токенов пользователя
        Расширенная функциональность
        """
        try:
            # Получаем все токены пользователя
            user_tokens = await self.token_repository.get_by_user_id(str(user_id))

            if not user_tokens:
                return {
                    "success": True,
                    "message": "У пользователя нет активных токенов",
                    "data": {
                        "user_id": str(user_id),
                        "revoked_count": 0
                    }
                }

            # Отзываем все токены
            revoked_count = 0
            for token_record in user_tokens:
                if not token_record.get("is_revoked", False):
                    success = await self.token_repository.revoke_token(token_record["token"])
                    if success:
                        revoked_count += 1

            return {
                "success": True,
                "message": f"Отозвано {revoked_count} токенов пользователя",
                "data": {
                    "user_id": str(user_id),
                    "revoked_count": revoked_count,
                    "total_tokens": len(user_tokens),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

        except Exception as e:
            raise DatabaseException(
                f"Ошибка при отзыве токенов пользователя: {str(e)}")

    async def get_user_tokens_info(self, user_id: UUID) -> Dict[str, Any]:
        """
        Получение информации о токенах пользователя
        Расширенная функциональность
        """
        try:
            # Получаем все токены пользователя
            user_tokens = await self.token_repository.get_by_user_id(str(user_id))

            if not user_tokens:
                return {
                    "success": True,
                    "data": {
                        "user_id": str(user_id),
                        "total_tokens": 0,
                        "active_tokens": 0,
                        "expired_tokens": 0,
                        "revoked_tokens": 0,
                        "tokens": []
                    }
                }

            current_time = datetime.utcnow()

            active_tokens = []
            expired_tokens = []
            revoked_tokens = []

            for token_record in user_tokens:
                token_info = {
                    "token_id": token_record.get("id"),
                    "token_type": token_record.get("token_type"),
                    "created_at": token_record.get("created_at").isoformat() if token_record.get("created_at") else None,
                    "expires_at": token_record.get("expires_at").isoformat() if token_record.get("expires_at") else None,
                    "is_revoked": token_record.get("is_revoked", False)
                }

                if token_record.get("is_revoked", False):
                    revoked_tokens.append(token_info)
                elif token_record.get("expires_at") and current_time > token_record["expires_at"]:
                    expired_tokens.append(token_info)
                else:
                    active_tokens.append(token_info)

            return {
                "success": True,
                "data": {
                    "user_id": str(user_id),
                    "total_tokens": len(user_tokens),
                    "active_tokens": len(active_tokens),
                    "expired_tokens": len(expired_tokens),
                    "revoked_tokens": len(revoked_tokens),
                    "tokens": {
                        "active": active_tokens,
                        "expired": expired_tokens,
                        "revoked": revoked_tokens
                    }
                }
            }

        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении информации о токенах: {str(e)}")

    async def _cleanup_old_revoked_tokens(self) -> int:
        """Очистка старых отозванных токенов (старше 7 дней)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            # В реальном приложении здесь был бы SQL запрос
            # Для заглушки возвращаем 0
            return 0
        except Exception:
            return 0

    async def _cleanup_unused_tokens(self) -> int:
        """Очистка неиспользуемых токенов (старше 30 дней)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            # В реальном приложении здесь был бы SQL запрос
            # Для заглушки возвращаем 0
            return 0
        except Exception:
            return 0
