"""
Репозиторий для работы с пользователями
Мигрирован из старого репозитория с async поддержкой и Clean Architecture
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm.query import Query

from ...schemas.requests import UserListRequestDTO, ListUsersRequestDTO
from ...schemas.responses import UserResponseDTO, UsersListResponseDTO
from ...interfaces.user import UserRepositoryInterface
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)

# Импорт реальных моделей (заменить на ваши модели)
try:
    from backend.user_service.src.models import User
except ImportError:
    # Временная заглушка для моделей
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


class UserRepository(UserRepositoryInterface):
    """Репозиторий для работы с пользователями"""

    def __init__(self, db_session: Session, **kwargs):
        self.db = db_session

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Получение пользователя по ID"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            return user
        except ValueError:
            return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.db.query(User).filter(User.email == email.lower()).first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        return self.db.query(User).filter(User.username == username.lower()).first()

    async def create(self, user_data: Dict[str, Any]) -> User:
        """Создание пользователя"""
        try:
            # Подготовка данных
            if 'email' in user_data:
                user_data['email'] = user_data['email'].lower().strip()
            if 'username' in user_data and user_data['username']:
                user_data['username'] = user_data['username'].lower().strip()

            user = User(**user_data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при создании пользователя: {str(e)}")

    async def update(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Обновление пользователя"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                return None

            # Обновляем поля пользователя
            for field, value in updates.items():
                if hasattr(user, field):
                    # Специальная обработка для email и username
                    if field == 'email' and value:
                        value = value.lower().strip()
                    elif field == 'username' and value:
                        value = value.lower().strip()
                    setattr(user, field, value)

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

    async def delete(self, user_id: str) -> bool:
        """Мягкое удаление пользователя"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                return False

            # Мягкое удаление - деактивация
            user.is_active = False
            user.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except ValueError:
            return False
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при удалении пользователя: {str(e)}")

    async def update_login_info(self, user_id: str, login_info: Dict[str, Any]) -> Optional[User]:
        """Обновление информации о входе"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                return None

            # Обновляем информацию о входе
            for field, value in login_info.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            user.last_login_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            return user
        except ValueError:
            return None
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при обновлении информации о входе: {str(e)}")

    async def check_email_exists(self, email: str) -> bool:
        """Проверка существования email"""
        email = email.lower().strip()
        user = self.db.query(User).filter(User.email == email).first()
        return user is not None

    async def check_username_exists(self, username: str) -> bool:
        """Проверка существования username"""
        if not username:
            return False
        username = username.lower().strip()
        user = self.db.query(User).filter(User.username == username).first()
        return user is not None

    async def get_users_by_email_pattern(self, email_pattern: str) -> List[User]:
        """Поиск пользователей по похожим email"""
        email_pattern = email_pattern.lower().strip()
        return self.db.query(User).filter(
            User.email.ilike(f"%{email_pattern}%")
        ).limit(10).all()

    async def get_failed_login_attempts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение неудачных попыток входа (заглушка)"""
        # В реальном приложении здесь была бы таблица с попытками входа
        return []

    async def get_login_history(self, user_id: str, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение истории входов"""
        try:
            uuid_id = UUID(user_id)
            cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)

            # В реальном приложении здесь была бы отдельная таблица входов
            # Для заглушки возвращаем последние входы пользователя
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                return []

            history = []
            if user.last_login_at:
                history.append({
                    "timestamp": user.last_login_at.isoformat(),
                    "ip_address": "unknown",  # В реальном приложении сохранять IP
                    "user_agent": "unknown",  # В реальном приложении сохранять User Agent
                    "success": True,
                    "location": "Unknown"
                })

            return history[:limit]
        except ValueError:
            return []

    async def get_login_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Получение статистики входов"""
        try:
            uuid_id = UUID(user_id)
            cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)

            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                return {}

            # Базовая статистика
            total_logins = 1 if user.last_login_at else 0
            successful_logins = total_logins
            failed_attempts = 0  # В реальном приложении считать из таблицы попыток

            return {
                "total_logins": total_logins,
                "successful_logins": successful_logins,
                "failed_attempts": failed_attempts,
                "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
                "period_days": days
            }
        except ValueError:
            return {}

    async def get_suspicious_activity(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение подозрительной активности (заглушка)"""
        # В реальном приложении здесь был бы анализ паттернов входов
        return []

    async def get_user_activity(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Получение активности пользователя"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                raise NotFoundException(
                    f"Пользователь с ID {user_id} не найден")

            activity = {
                "user_id": user_id,
                "period_days": days,
                "is_active": user.is_active,
                "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
                "account_created": user.created_at.isoformat(),
                "account_status": "active" if user.is_active else "inactive",
                "login_count": 1 if user.last_login_at else 0,
                "failed_attempts": 0  # В реальном приложении считать из таблицы попыток
            }

            return activity
        except ValueError:
            raise ValidationException("Некорректный формат user_id")

    async def search_users(self, search_term: str, limit: int = 20) -> List[User]:
        """Поиск пользователей"""
        search_term = search_term.lower().strip()
        return self.db.query(User).filter(
            or_(
                User.email.ilike(f"%{search_term}%"),
                User.first_name.ilike(f"%{search_term}%"),
                User.last_name.ilike(f"%{search_term}%"),
                User.username.ilike(f"%{search_term}%") if hasattr(
                    User, 'username') else False
            )
        ).filter(User.is_active == True).limit(limit).all()

    # === Методы для блокировки/разблокировки ===

    async def get_locked_users(self, limit: int = 100) -> List[User]:
        """Получение заблокированных пользователей"""
        return self.db.query(User).filter(
            and_(
                User.is_locked == True,
                User.locked_until > datetime.utcnow()
            )
        ).limit(limit).all()

    async def get_expired_locked_users(self) -> List[User]:
        """Получение пользователей с истекшей блокировкой"""
        return self.db.query(User).filter(
            and_(
                User.is_locked == True,
                User.locked_until <= datetime.utcnow()
            )
        ).all()

    async def get_recent_login_attempts(self, user_id: str, minutes: int = 15, limit: int = 1000) -> List[Dict[str, Any]]:
        """Получение недавних попыток входа (заглушка)"""
        # В реальном приложении здесь был бы анализ таблицы попыток входа
        return []

    # === Методы для пагинации и списков ===

    async def list_users_with_pagination(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        role: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """Получение списка пользователей с пагинацией и фильтрацией"""
        try:
            # Базовый запрос
            query = self.db.query(User)

            # Применяем фильтры
            if search:
                search_term = search.lower().strip()
                query = query.filter(
                    or_(
                        User.email.ilike(f"%{search_term}%"),
                        User.first_name.ilike(f"%{search_term}%"),
                        User.last_name.ilike(f"%{search_term}%"),
                        User.username.ilike(f"%{search_term}%") if hasattr(
                            User, 'username') else False
                    )
                )

            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            if is_verified is not None and hasattr(User, 'is_verified'):
                query = query.filter(User.is_verified == is_verified)

            if role:
                query = query.filter(User.role == role)

            # Подсчет общего количества
            total = query.count()

            # Сортировка
            if hasattr(User, sort_by):
                sort_field = getattr(User, sort_by)
                if sort_order.lower() == "desc":
                    query = query.order_by(desc(sort_field))
                else:
                    query = query.order_by(asc(sort_field))
            else:
                query = query.order_by(desc(User.created_at))

            # Пагинация
            offset = (page - 1) * per_page
            users = query.offset(offset).limit(per_page).all()

            # Форматирование результата
            users_data = []
            for user in users:
                user_dict = {
                    "id": user.id,
                    "email": user.email,
                    "username": getattr(user, 'username', None),
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": getattr(user, 'phone', None),
                    "role": user.role,
                    "is_active": user.is_active,
                    "is_verified": getattr(user, 'is_verified', False),
                    "created_at": user.created_at,
                    "updated_at": user.updated_at
                }
                users_data.append(user_dict)

            return {
                "users": users_data,
                "total": total,
                "page": page,
                "per_page": per_page
            }

        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении списка пользователей: {str(e)}")

    # === Методы для ролей (заглушки - будут реализованы с UserRoleRepository) ===

    async def get_user_roles(self, user_id: str) -> List[Any]:
        """Получение ролей пользователя (заглушка)"""
        # Будет реализовано через UserRoleRepository
        return []

    async def add_role_to_user(self, user_id: str, role: Any) -> bool:
        """Добавление роли пользователю (заглушка)"""
        # Будет реализовано через UserRoleRepository
        return True

    async def remove_role_from_user(self, user_id: str, role: Any) -> bool:
        """Удаление роли у пользователя (заглушка)"""
        # Будет реализовано через UserRoleRepository
        return True

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Получение разрешений пользователя (заглушка)"""
        # Будет реализовано через систему ролей
        return ["read", "write"]

    async def check_user_permission(self, user_id: str, permission: str) -> bool:
        """Проверка разрешения пользователя (заглушка)"""
        # Будет реализовано через систему ролей
        return True

    async def lock_user(self, user_id: str, reason: str = None, duration_hours: int = None) -> bool:
        """Блокировка пользователя"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                return False

            user.is_locked = True
            user.lock_reason = reason or "Не указана причина"

            if duration_hours:
                from datetime import timedelta
                user.locked_until = datetime.utcnow() + timedelta(hours=duration_hours)
            else:
                user.locked_until = None  # Бессрочная блокировка

            user.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except ValueError:
            return False
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(
                f"Ошибка при блокировке пользователя: {str(e)}")

    async def unlock_user(self, user_id: str) -> bool:
        """Разблокировка пользователя"""
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
                f"Ошибка при разблокировке пользователя: {str(e)}")

    async def is_user_locked(self, user_id: str) -> bool:
        """Проверка статуса блокировки пользователя"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                return False

            # Проверяем, заблокирован ли пользователь и не истекла ли блокировка
            if user.is_locked and user.locked_until:
                if datetime.utcnow() > user.locked_until:
                    # Время блокировки истекло, автоматически разблокируем
                    await self.unlock_user(user_id)
                    return False
                return True
            elif user.is_locked:
                # Бессрочная блокировка
                return True

            return False
        except ValueError:
            return False

    async def get_user_lock_status(self, user_id: str) -> Dict[str, Any]:
        """Получение статуса блокировки пользователя"""
        try:
            uuid_id = UUID(user_id)
            user = self.db.query(User).filter(User.id == uuid_id).first()
            if not user:
                return {"is_locked": False}

            return {
                "is_locked": user.is_locked,
                "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                "lock_reason": user.lock_reason,
                "is_expired": user.locked_until and datetime.utcnow() > user.locked_until if user.locked_until else False
            }
        except ValueError:
            return {"is_locked": False}
