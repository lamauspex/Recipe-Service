
"""
Класс, ответственный за базовые операции с пользователями
(блокировки, активации, изменение статусов и ролей)
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from user_service.models import User
from user_service.schemas.user_roles import UserRole
from user_service.repository import AdminRepository


class UserManagementService:
    """Сервис для работы с пользователями"""

    def __init__(self, db_session):
        self.repository = AdminRepository(db_session)

    def change_user_status(
        self,
        user_id: UUID,
        action: str
    ) -> bool:
        """Изменение статуса пользователя"""

        update_data = {"is_active": True if action in [
            'activate', 'unblock'] else False}

        result = self.repository.update_user(
            user_id,
            update_data
        )
        return result is not None

    def soft_delete_user(
        self,
        user_id: UUID
    ) -> bool:
        """Мягкое удаление пользователя"""

        result = self.repository.delete_user(
            user_id,
            {
                "is_active": False,
                "is_deleted": True,
                "updated_at": datetime.now(timezone.utc)
            }
        )
        return result is not None

    def bulk_user_action(
        self,
        action: str,
        user_ids: List[UUID]
    ) -> dict:
        """Массовое действие над пользователями"""

        success_count = 0
        failed_count = 0

        for user_id in user_ids:
            if action in ["activate", "unblock"]:
                result = self.change_user_status(user_id, "activate")
            elif action in ["deactivate", "block"]:
                result = self.change_user_status(user_id, "deactivate")
            else:
                failed_count += 1
                continue

            if result:
                success_count += 1
            else:
                failed_count += 1

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "total_count": len(user_ids)
        }

    def get_users_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Получение пользователей с фильтрацией"""

        query = self.repository.db.query(User)

        if search:
            query = query.filter(
                User.user_name.contains(search) |
                User.email.contains(search) |
                User.full_name.contains(search)
            )

        if role:
            query = query.filter(User.role == role)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.offset(skip).limit(limit).all()
