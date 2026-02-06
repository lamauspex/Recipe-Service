"""
Token Repository - полная миграция из старого репозитория
Реализация с async поддержкой и расширенной функциональностью
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm.query import Query

from ...interfaces.token import TokenRepositoryInterface
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)

# Импорт реальных моделей (заменить на ваши модели)
try:
    from backend.user_service.src.models import RefreshToken
except ImportError:
    # Временная заглушка для модели RefreshToken
    class RefreshToken:
        def __init__(self):
            self.id = "mock_token_id"
            self.user_id = "mock_user_id"
            self.token = "mock_token"
            self.token_type = "refresh"
            self.expires_at = datetime.utcnow() + timedelta(days=7)
            self.created_at = datetime.utcnow()
            self.is_revoked = False


class TokenRepository(TokenRepositoryInterface):
    """Репозиторий для работы с токенами"""

    def __init__(self, db_session: Session, **kwargs):
        self.db = db_session

    async def create(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание токена"""
        try:
            # Подготовка данных токена
            token_type = token_data.get("token_type", "refresh")
            expires_at = token_data.get("expires_at")

            if not expires_at:
                # Устанавливаем стандартное время истечения
                if token_type == "refresh":
                    expires_at = datetime.utcnow() + timedelta(days=7)
                else:
                    expires_at = datetime.utcnow() + timedelta(hours=1)

            # Создаем токен
            token = RefreshToken(
                user_id=token_data["user_id"],
                token=token_data["token"],
                token_type=token_type,
                expires_at=expires_at,
                created_at=datetime.utcnow(),
                is_revoked=False
            )

            self.db.add(token)
            self.db.commit()
            self.db.refresh(token)

            return {
                "id": str(token.id),
                "user_id": token.user_id,
                "token": token.token,
                "token_type": token.token_type,
                "expires_at": token.expires_at,
                "created_at": token.created_at,
                "is_revoked": token.is_revoked
            }
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Ошибка при создании токена: {str(e)}")

    async def get_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Получение токена по значению"""
        try:
            token_record = self.db.query(RefreshToken).filter(
                RefreshToken.token == token
            ).first()

            if not token_record:
                return None

            return {
                "id": str(token_record.id),
                "user_id": token_record.user_id,
                "token": token_record.token,
                "token_type": token_record.token_type,
                "expires_at": token_record.expires_at,
                "created_at": token_record.created_at,
                "is_revoked": token_record.is_revoked
            }
        except Exception as e:
            raise DatabaseException(f"Ошибка при получении токена: {str(e)}")

    async def get_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение токенов пользователя"""
        try:
            uuid_user_id = UUID(user_id)
            tokens = self.db.query(RefreshToken).filter(
                RefreshToken.user_id == uuid_user_id
            ).order_by(desc(RefreshToken.created_at)).all()

            return [
                {
                    "id": str(token.id),
                    "user_id": str(token.user_id),
                    "token": token.token,
                    "token_type": token.token_type,
                    "expires_at": token.expires_at,
                    "created_at": token.created_at,
                    "is_revoked": token.is_revoked
                }
                for token in tokens
            ]
        except ValueError:
            return []
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении токенов пользователя: {str(e)}")

    async def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""
        try:
            token_record = self.db.query(RefreshToken).filter(
                RefreshToken.token == token
            ).first()

            if not token_record:
                return False

            # Проверяем, не отозван ли уже токен
            if token_record.is_revoked:
                return True

            token_record.is_revoked = True
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Ошибка при отзыве токена: {str(e)}")

    async def revoke_all_user_tokens(self, user_id: str) -> bool:
        """Отзыв всех токенов пользователя"""
        try:
            uuid_user_id = UUID(user_id)

            # Обновляем все токены пользователя
            updated_count = self.db.query(RefreshToken).filter(
                and_(
                    RefreshToken.user_id == uuid_user_id,
                    RefreshToken.is_revoked == False
                )
            ).update({"is_revoked": True})

            self.db.commit()
            return updated_count > 0
        except ValueError:
            return False
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при отзыве токенов пользователя: {str(e)}")

    async def get_valid_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Получение валидного токена"""
        try:
            current_time = datetime.now(timezone.utc)

            token_record = self.db.query(RefreshToken).filter(
                and_(
                    RefreshToken.token == token,
                    RefreshToken.is_revoked == False,
                    RefreshToken.expires_at > current_time
                )
            ).first()

            if not token_record:
                return None

            return {
                "id": str(token_record.id),
                "user_id": str(token_record.user_id),
                "token": token_record.token,
                "token_type": token_record.token_type,
                "expires_at": token_record.expires_at,
                "created_at": token_record.created_at,
                "is_revoked": token_record.is_revoked
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при проверке валидности токена: {str(e)}")

    async def cleanup_expired_tokens(self) -> int:
        """Очистка истекших токенов"""
        try:
            current_time = datetime.now(timezone.utc)

            # Удаляем истекшие токены
            expired_count = self.db.query(RefreshToken).filter(
                RefreshToken.expires_at < current_time
            ).delete()

            self.db.commit()
            return expired_count
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при очистке истекших токенов: {str(e)}")

    # === Расширенная функциональность ===

    async def create_refresh_token(
        self,
        user_id: str,
        token: str,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Создание refresh токена с отзывом старых"""
        try:
            uuid_user_id = UUID(user_id)

            # Отзываем старые refresh токены пользователя
            await self.revoke_all_user_tokens(user_id)

            # Устанавливаем время истечения
            if not expires_at:
                expires_at = datetime.utcnow() + timedelta(days=7)

            # Создаем новый токен
            token_data = {
                "user_id": str(uuid_user_id),
                "token": token,
                "token_type": "refresh",
                "expires_at": expires_at
            }

            return await self.create(token_data)
        except ValueError:
            raise ValidationException("Некорректный формат user_id")

    async def get_expired_tokens(self, days_old: int = 30) -> List[Dict[str, Any]]:
        """Получение токенов, истекших более чем days_old дней назад"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            expired_tokens = self.db.query(RefreshToken).filter(
                RefreshToken.expires_at < cutoff_date
            ).all()

            return [
                {
                    "id": str(token.id),
                    "user_id": str(token.user_id),
                    # Частично скрываем токен
                    "token": token.token[:10] + "...",
                    "token_type": token.token_type,
                    "expires_at": token.expires_at,
                    "created_at": token.created_at,
                    "is_revoked": token.is_revoked
                }
                for token in expired_tokens
            ]
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении истекших токенов: {str(e)}")

    async def get_revoked_tokens(self, days_old: int = 7) -> List[Dict[str, Any]]:
        """Получение отозванных токенов"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            revoked_tokens = self.db.query(RefreshToken).filter(
                and_(
                    RefreshToken.is_revoked == True,
                    RefreshToken.created_at >= cutoff_date
                )
            ).order_by(desc(RefreshToken.created_at)).all()

            return [
                {
                    "id": str(token.id),
                    "user_id": str(token.user_id),
                    "token": token.token[:10] + "...",
                    "token_type": token.token_type,
                    "expires_at": token.expires_at,
                    "created_at": token.created_at,
                    "is_revoked": token.is_revoked
                }
                for token in revoked_tokens
            ]
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении отозванных токенов: {str(e)}")

    async def get_token_statistics(self) -> Dict[str, Any]:
        """Получение статистики по токенам"""
        try:
            current_time = datetime.now(timezone.utc)

            # Общая статистика
            total_tokens = self.db.query(RefreshToken).count()
            active_tokens = self.db.query(RefreshToken).filter(
                and_(
                    RefreshToken.is_revoked == False,
                    RefreshToken.expires_at > current_time
                )
            ).count()
            expired_tokens = self.db.query(RefreshToken).filter(
                RefreshToken.expires_at < current_time
            ).count()
            revoked_tokens = self.db.query(RefreshToken).filter(
                RefreshToken.is_revoked == True
            ).count()

            # Статистика по типам токенов
            refresh_tokens = self.db.query(RefreshToken).filter(
                RefreshToken.token_type == "refresh"
            ).count()

            # Статистика по пользователям
            unique_users = self.db.query(
                RefreshToken.user_id).distinct().count()

            # Среднее время жизни токенов
            avg_lifetime = self.db.query(
                RefreshToken.expires_at - RefreshToken.created_at
            ).filter(
                RefreshToken.token_type == "refresh"
            ).all()

            avg_lifetime_hours = 0
            if avg_lifetime:
                total_seconds = sum((life.total_seconds()
                                    for life in avg_lifetime), 0)
                avg_lifetime_hours = total_seconds / len(avg_lifetime) / 3600

            return {
                "total_tokens": total_tokens,
                "active_tokens": active_tokens,
                "expired_tokens": expired_tokens,
                "revoked_tokens": revoked_tokens,
                "refresh_tokens": refresh_tokens,
                "unique_users_with_tokens": unique_users,
                "average_lifetime_hours": round(avg_lifetime_hours, 2),
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении статистики токенов: {str(e)}")

    async def cleanup_old_revoked_tokens(self, days_old: int = 7) -> int:
        """Очистка старых отозванных токенов"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            deleted_count = self.db.query(RefreshToken).filter(
                and_(
                    RefreshToken.is_revoked == True,
                    RefreshToken.created_at < cutoff_date
                )
            ).delete()

            self.db.commit()
            return deleted_count
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при очистке старых отозванных токенов: {str(e)}")

    async def cleanup_unused_tokens(self, days_old: int = 30) -> int:
        """Очистка неиспользуемых токенов"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            # Удаляем токены, которые были созданы давно и не использовались
            deleted_count = self.db.query(RefreshToken).filter(
                and_(
                    RefreshToken.created_at < cutoff_date,
                    RefreshToken.is_revoked == False
                )
            ).delete()

            self.db.commit()
            return deleted_count
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при очистке неиспользуемых токенов: {str(e)}")

    async def bulk_revoke_tokens(self, tokens: List[str]) -> Dict[str, Any]:
        """Массовый отзыв токенов"""
        try:
            revoked_count = 0
            errors = []

            for token in tokens:
                try:
                    if await self.revoke_token(token):
                        revoked_count += 1
                    else:
                        errors.append(f"Токен {token[:10]}... не найден")
                except Exception as e:
                    errors.append(
                        f"Ошибка отзыва токена {token[:10]}...: {str(e)}")

            return {
                "success": True,
                "revoked_count": revoked_count,
                "errors": errors,
                "total_attempted": len(tokens)
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при массовом отзыве токенов: {str(e)}")

    async def get_user_token_count(self, user_id: str) -> Dict[str, Any]:
        """Получение количества токенов пользователя"""
        try:
            uuid_user_id = UUID(user_id)
            current_time = datetime.now(timezone.utc)

            # Активные токены
            active_tokens = self.db.query(RefreshToken).filter(
                and_(
                    RefreshToken.user_id == uuid_user_id,
                    RefreshToken.is_revoked == False,
                    RefreshToken.expires_at > current_time
                )
            ).count()

            # Истекшие токены
            expired_tokens = self.db.query(RefreshToken).filter(
                and_(
                    RefreshToken.user_id == uuid_user_id,
                    RefreshToken.expires_at < current_time
                )
            ).count()

            # Отозванные токены
            revoked_tokens = self.db.query(RefreshToken).filter(
                and_(
                    RefreshToken.user_id == uuid_user_id,
                    RefreshToken.is_revoked == True
                )
            ).count()

            # Всего токенов
            total_tokens = active_tokens + expired_tokens + revoked_tokens

            return {
                "user_id": user_id,
                "total_tokens": total_tokens,
                "active_tokens": active_tokens,
                "expired_tokens": expired_tokens,
                "revoked_tokens": revoked_tokens,
                "last_token_created": self.db.query(RefreshToken).filter(
                    RefreshToken.user_id == uuid_user_id
                ).order_by(desc(RefreshToken.created_at)).first().created_at.isoformat() if total_tokens > 0 else None
            }
        except ValueError:
            return {"user_id": user_id, "total_tokens": 0, "active_tokens": 0, "expired_tokens": 0, "revoked_tokens": 0}
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении количества токенов пользователя: {str(e)}")
