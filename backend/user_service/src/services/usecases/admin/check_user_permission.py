
from ..base import BaseUsecase


class CheckUserPermission(BaseUsecase):
    """Usecase для проверки разрешения пользователя"""

    async def check_user_permission(self, user_id: UUID, permission: str) -> Dict[str, Any]:

    try:
        user = self.db_session.query(User).filter(
            User.id == user_id).first()

        if not user:
            return ResponseBuilder.not_found("Пользователь")

        has_permission = self._user_has_permission(user, permission)

        return self._handle_success(
            "Проверка разрешения выполнена",
            data={
                "user_id": str(user_id),
                "permission": permission,
                "has_permission": has_permission
            }
        )

    except Exception as e:
        return self._handle_error(e, "проверки разрешения")
