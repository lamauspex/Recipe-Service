"""
Класс, ответственный за базовые операции с пользователями
(блокировки, активации, изменение статусов и ролей)
"""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from backend.user_service.src.models import User
from backend.user_service.src.schemas.user_roles import UserRole
from backend.user_service.src.schemas import UserResponse
from backend.user_service.src.repository import AdminRepository


class UserManagementService:
    """Сервис для работы с пользователями"""

    def __init__(self, db_session):
        self.repository = AdminRepository(db_session)

    def change_user_status(
        self,
        user_id: UUID,
        action: str,
        reason: Optional[str] = None
    ) -> dict:
        """Изменение статуса пользователя - возвращает готовый ответ"""

        update_data = {"is_active": True if action in [
            'activate', 'unblock'] else False}

        # Добавляем причину в обновление, если указана
        if reason:
            update_data["status_change_reason"] = reason
            update_data["status_changed_at"] = datetime.now(timezone.utc)

        result = self.repository.update_user(
            user_id,
            update_data
        )

        if result:
            return {
                "message": f"Статус пользователя изменен на: {action}",
                "success": True
            }
        else:
            return {
                "error": f"Не удалось изменить статус пользователя",
                "success": False
            }

    def soft_delete_user(
        self,
        user_id: UUID,
        reason: Optional[str] = None
    ) -> dict:
        """Мягкое удаление пользователя - возвращает готовый ответ"""

        update_data = {
            "is_active": False,
            "is_deleted": True,
            "updated_at": datetime.now(timezone.utc)
        }

        # Добавляем причину удаления, если указана
        if reason:
            update_data["deletion_reason"] = reason
            update_data["deleted_at"] = datetime.now(timezone.utc)

        result = self.repository.delete_user(
            user_id,
            update_data
        )

        if result:
            return {
                "message": "Пользователь успешно удален",
                "success": True
            }
        else:
            return {
                "error": f"Не удалось удалить пользователя",
                "success": False
            }

    def bulk_user_action(
        self,
        action: str,
        user_ids: List[UUID],
        reason: Optional[str] = None,
        admin_id: Optional[str] = None
    ) -> dict:
        """Массовое действие над пользователями - возвращает готовый ответ"""

        success_count = 0
        failed_count = 0

        for user_id in user_ids:
            if action in ["activate", "unblock"]:
                result = self.change_user_status(user_id, "activate", reason)
            elif action in ["deactivate", "block"]:
                result = self.change_user_status(user_id, "deactivate", reason)
            elif action == "delete":
                result = self.soft_delete_user(user_id, reason)
            else:
                failed_count += 1
                continue

            if result.get("success", False):
                success_count += 1
            else:
                failed_count += 1

        return {
            "message": (
                f"Массовое действие '{action}' выполнено для "
                f"{len(user_ids)} пользователей"
            ),
            "details": {
                "success_count": success_count,
                "failed_count": failed_count,
                "total_count": len(user_ids)
            },
            "success": True
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

    def get_users_with_filters_response(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[UserResponse]:
        """Получение пользователей с фильтрацией и валидацией роли - возвращает схемы"""

        # Валидация роли в сервисе
        role_enum = None
        if role:
            try:
                role_enum = UserRole(role)
            except ValueError:
                raise ValueError(
                    f"Роль '{role}' не существует. Доступные роли: "
                    f"{', '.join([r.value for r in UserRole])}"
                )

        # Получаем пользователей
        users = self.get_users_with_filters(
            skip=skip,
            limit=limit,
            search=search,
            role=role_enum,
            is_active=is_active
        )

        # Конвертируем в схемы в сервисе
        return [UserResponse.model_validate(user) for user in users]
