"""
Сервис управления пользователями
Обновлен для использования базового класса
"""

from datetime import datetime, timezone
from uuid import UUID
from typing import Dict, Any, Optional

from backend.user_service.src.models import User
from backend.user_service.src.exceptions.base import NotFoundException
from common.base_service import BaseService
from common.response_builder import ResponseBuilder


class ManagementService(BaseService):
    """Сервис для управления пользователями"""

    def __init__(self, db_session):
        super().__init__()
        self.db_session = db_session

    def get_all_users(
        self,
        page: int = 1,
        per_page: int = 10,
        search: str = None,
        is_active: bool = None,
        is_locked: bool = None
    ) -> Dict[str, Any]:
        """Получение всех пользователей с фильтрацией и пагинацией"""
        try:
            query = self.db_session.query(User)

            # Применяем фильтры
            if search:
                query = query.filter(
                    User.user_name.contains(search) |
                    User.email.contains(search) |
                    User.full_name.contains(search)
                )

            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            if is_locked is not None:
                query = query.filter(User.is_locked == is_locked)

            # Подсчитываем общее количество
            total = query.count()

            # Пагинация
            offset = (page - 1) * per_page
            users = query.offset(offset).limit(per_page).all()

            # Формируем данные
            user_list = []
            for user in users:
                user_list.append(self._serialize_user(user))

            return ResponseBuilder.paginated_response(
                items=user_list,
                total=total,
                page=page,
                per_page=per_page
            )

        except Exception as e:
            return self._handle_error(e, "получения списка пользователей")

    def get_user_by_id(self, user_id: UUID) -> Dict[str, Any]:
        """Получение пользователя по ID"""
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            return self._handle_success(
                "Пользователь найден",
                data=self._serialize_user(user, include_roles=True)
            )

        except Exception as e:
            return self._handle_error(e, "получения пользователя по ID")

    def update_user_status(self, user_id: UUID, status: str, reason: str = None) -> Dict[str, Any]:
        """Обновление статуса пользователя"""
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            if status == "activate":
                user.is_active = True
                user.is_locked = False
                message = "Пользователь активирован"
            elif status == "deactivate":
                user.is_active = False
                message = "Пользователь деактивирован"
            elif status == "lock":
                user.is_locked = True
                message = "Пользователь заблокирован"
            elif status == "unlock":
                user.is_locked = False
                user.lock_reason = None
                user.locked_until = None
                message = "Пользователь разблокирован"
            else:
                return ResponseBuilder.error(
                    "Неверный статус",
                    error_code="INVALID_STATUS",
                    details={"valid_statuses": [
                        "activate", "deactivate", "lock", "unlock"]}
                )

            user.updated_at = datetime.now(timezone.utc)

            if reason:
                user.lock_reason = reason

            self.db_session.commit()

            return self._handle_success(message)

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "обновления статуса пользователя")

    def delete_user(self, user_id: UUID) -> Dict[str, Any]:
        """Удаление пользователя (мягкое удаление)"""
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            # Мягкое удаление - деактивация
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)

            self.db_session.commit()

            return self._handle_success("Пользователь удален (деактивирован)")

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "удаления пользователя")

    def get_user_activity(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Получение активности пользователя"""
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            # Получаем информацию об активности
            activity_data = {
                "user_id": str(user_id),
                "period_days": days,
                "last_login": user.last_login_at.isoformat() if user.last_login_at else None,
                "last_login_ip": user.last_login_ip,
                "account_created": user.created_at.isoformat(),
                "last_updated": user.updated_at.isoformat(),
                "email_verified": user.email_verified,
                "is_locked": user.is_locked,
                "locked_until": user.locked_until.isoformat() if user.locked_until else None,
                "lock_reason": user.lock_reason
            }

            return self._handle_success(
                "Активность пользователя получена",
                data=activity_data
            )

        except Exception as e:
            return self._handle_error(e, "получения активности пользователя")

    def search_users(self, search_term: str, limit: int = 20) -> Dict[str, Any]:
        """Поиск пользователей"""
        try:
            if not search_term.strip():
                return ResponseBuilder.error(
                    "Поисковый запрос не может быть пустым",
                    error_code="EMPTY_SEARCH_TERM"
                )

            users = self.db_session.query(User).filter(
                User.user_name.contains(search_term) |
                User.email.contains(search_term) |
                User.full_name.contains(search_term)
            ).limit(limit).all()

            user_list = [self._serialize_user(user) for user in users]

            return self._handle_success(
                "Поиск пользователей выполнен",
                data={
                    "search_term": search_term,
                    "results": user_list,
                    "total_found": len(user_list)
                }
            )

        except Exception as e:
            return self._handle_error(e, "поиска пользователей")

    def _serialize_user(self, user: User, include_roles: bool = False) -> Dict[str, Any]:
        """Сериализация пользователя для ответа API"""
        data = {
            "id": str(user.id),
            "user_name": user.user_name,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "is_locked": user.is_locked,
            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
            "lock_reason": user.lock_reason,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "last_login_ip": user.last_login_ip,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }

        if include_roles and hasattr(user, 'roles'):
            data["roles"] = [
                {"id": str(role.id), "name": role.name,
                 "description": role.description}
                for role in user.roles
            ]

        return data
