"""
Admin Repository - репозиторий для административных операций
Создан на основе функциональности из старого admin_repo.py
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from ...interfaces.admin import AdminRepositoryInterface
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)

# Импорт реальных моделей (заменить на ваши модели)
try:
    from backend.user_service.src.models import User
except ImportError:
    # Временная заглушка для модели User
    class User:
        def __init__(self):
            self.id = "mock_id"
            self.email = "mock@example.com"
            self.first_name = "Mock"
            self.last_name = "User"
            self.phone = None
            self.username = None
            self.hashed_password = "mock_hash"
            self.role = "user"
            self.is_active = True
            self.is_verified = False
            self.is_locked = False
            self.locked_until = None
            self.lock_reason = None
            self.last_login_at = None
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()


class AdminRepository(AdminRepositoryInterface):
    """Репозиторий для административных операций"""

    def __init__(self, db_session: Session, **kwargs):
        self.db = db_session

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Получение пользователя по ID"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            return user
        except ValueError:
            return None

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей"""
        try:
            return self.db.query(User).offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении списка пользователей: {str(e)}")

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка активных пользователей"""
        try:
            return self.db.query(User).filter(
                User.is_active == True
            ).offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении списка активных пользователей: {str(e)}")

    async def delete_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Мягкое удаление пользователя с обновлением данных"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()

            if not user:
                return False

            # Обновляем поля пользователя для мягкого удаления
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            user.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except ValueError:
            return False
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при удалении пользователя: {str(e)}")

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Обновление пользователя и возврат обновленного объекта"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()

            if not user:
                return None

            # Обновляем поля пользователя
            for key, value in update_data.items():
                if hasattr(user, key):
                    # Специальная обработка для email и username
                    if key == 'email' and value:
                        value = value.lower().strip()
                    elif key == 'username' and value:
                        value = value.lower().strip()
                    setattr(user, key, value)

            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            return user
        except ValueError:
            return None
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при обновлении пользователя: {str(e)}")

    # === Расширенная административная функциональность ===

    async def get_users_statistics(self) -> Dict[str, Any]:
        """Получение статистики по пользователям"""
        try:
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(
                User.is_active == True).count()
            inactive_users = total_users - active_users
            verified_users = self.db.query(User).filter(
                and_(User.is_active == True, User.is_verified == True)
            ).count() if hasattr(User, 'is_verified') else 0
            locked_users = self.db.query(User).filter(
                User.is_locked == True).count()

            # Статистика по ролям
            role_stats = self.db.query(
                User.role,
                func.count(User.id).label('count')
            ).filter(User.is_active == True).group_by(User.role).all()

            role_distribution = {role: count for role, count in role_stats}

            # Статистика по датам регистрации (последние 30 дней)
            thirty_days_ago = datetime.utcnow() - datetime.timedelta(days=30)
            new_users_last_30_days = self.db.query(User).filter(
                User.created_at >= thirty_days_ago
            ).count()

            return {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "verified_users": verified_users,
                "locked_users": locked_users,
                "new_users_last_30_days": new_users_last_30_days,
                "role_distribution": role_distribution,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении статистики пользователей: {str(e)}")

    async def search_users_admin(
        self,
        search_term: str,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[User], int]:
        """Расширенный поиск пользователей для администраторов"""
        try:
            query = self.db.query(User)

            # Текстовый поиск
            if search_term:
                search_term = search_term.lower().strip()
                query = query.filter(
                    or_(
                        User.email.ilike(f"%{search_term}%"),
                        User.first_name.ilike(f"%{search_term}%"),
                        User.last_name.ilike(f"%{search_term}%"),
                        User.username.ilike(f"%{search_term}%") if hasattr(
                            User, 'username') else False
                    )
                )

            # Применяем фильтры
            if filters:
                if filters.get('is_active') is not None:
                    query = query.filter(
                        User.is_active == filters['is_active'])
                if filters.get('is_verified') is not None and hasattr(User, 'is_verified'):
                    query = query.filter(
                        User.is_verified == filters['is_verified'])
                if filters.get('role'):
                    query = query.filter(User.role == filters['role'])
                if filters.get('is_locked') is not None:
                    query = query.filter(
                        User.is_locked == filters['is_locked'])

            # Подсчет общего количества
            total = query.count()

            # Сортировка и пагинация
            query = query.order_by(desc(User.created_at)
                                   ).offset(skip).limit(limit)
            users = query.all()

            return users, total
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при поиске пользователей: {str(e)}")

    async def get_users_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Получение пользователей за определенный период"""
        try:
            return self.db.query(User).filter(
                and_(
                    User.created_at >= start_date,
                    User.created_at <= end_date
                )
            ).order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении пользователей за период: {str(e)}")

    async def bulk_update_users(self, updates: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Массовое обновление пользователей"""
        try:
            updated_count = 0
            errors = []

            for user_id, user_updates in updates.items():
                try:
                    result = await self.update_user(user_id, user_updates)
                    if result:
                        updated_count += 1
                    else:
                        errors.append(f"Пользователь {user_id} не найден")
                except Exception as e:
                    errors.append(
                        f"Ошибка обновления пользователя {user_id}: {str(e)}")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors,
                "total_attempted": len(updates)
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при массовом обновлении пользователей: {str(e)}")

    async def get_inactive_users(self, days_inactive: int = 30) -> List[User]:
        """Получение неактивных пользователей"""
        try:
            cutoff_date = datetime.utcnow() - datetime.timedelta(days=days_inactive)
            return self.db.query(User).filter(
                and_(
                    User.is_active == True,
                    User.last_login_at < cutoff_date
                )
            ).order_by(desc(User.last_login_at)).all()
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении неактивных пользователей: {str(e)}")

    async def get_locked_users_admin(self) -> List[User]:
        """Получение заблокированных пользователей для администратора"""
        try:
            return self.db.query(User).filter(
                and_(
                    User.is_locked == True,
                    User.locked_until > datetime.utcnow()
                )
            ).order_by(desc(User.locked_until)).all()
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении заблокированных пользователей: {str(e)}")

    async def force_unlock_user(self, user_id: str) -> bool:
        """Принудительная разблокировка пользователя администратором"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                return False

            user.is_locked = False
            user.locked_until = None
            user.lock_reason = None
            user.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except ValueError:
            return False
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при принудительной разблокировке пользователя: {str(e)}")

    async def get_user_activity_summary(self, user_id: str) -> Dict[str, Any]:
        """Получение сводки активности пользователя для администратора"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                raise NotFoundException(
                    f"Пользователь с ID {user_id} не найден")

            # Базовая информация
            summary = {
                "user_id": user_id,
                "email": user.email,
                "is_active": user.is_active,
                "is_locked": user.is_locked,
                "account_created": user.created_at.isoformat(),
                "last_updated": user.updated_at.isoformat(),
                "last_login": user.last_login_at.isoformat() if user.last_login_at else None
            }

            # Дополнительная информация если есть поля
            if hasattr(user, 'is_verified'):
                summary["is_verified"] = user.is_verified
            if hasattr(user, 'phone'):
                summary["phone"] = user.phone
            if hasattr(user, 'username'):
                summary["username"] = user.username

            # Информация о блокировке
            if user.is_locked:
                summary["lock_info"] = {
                    "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                    "lock_reason": user.lock_reason
                }

            return summary
        except ValueError:
            raise ValidationException("Некорректный формат user_id")
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении сводки активности пользователя: {str(e)}")

    async def perform_maintenance_operations(self) -> Dict[str, Any]:
        """Выполнение операций обслуживания пользователей"""
        try:
            results = {
                "expired_locks_cleared": 0,
                "inactive_users_deactivated": 0,
                "total_operations": 0
            }

            # Очистка истекших блокировок
            expired_locks = self.db.query(User).filter(
                and_(
                    User.is_locked == True,
                    User.locked_until <= datetime.utcnow()
                )
            ).all()

            for user in expired_locks:
                user.is_locked = False
                user.locked_until = None
                user.lock_reason = None
                user.updated_at = datetime.utcnow()
                results["expired_locks_cleared"] += 1

            # Деактивация неактивных пользователей (старше 1 года)
            one_year_ago = datetime.utcnow() - datetime.timedelta(days=365)
            inactive_users = self.db.query(User).filter(
                and_(
                    User.is_active == True,
                    User.last_login_at < one_year_ago
                )
            ).all()

            for user in inactive_users:
                user.is_active = False
                user.updated_at = datetime.utcnow()
                results["inactive_users_deactivated"] += 1

            results["total_operations"] = results["expired_locks_cleared"] + \
                results["inactive_users_deactivated"]

            self.db.commit()

            return {
                "success": True,
                "results": results,
                "performed_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при выполнении операций обслуживания: {str(e)}")
