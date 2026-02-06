
from ..base import BaseUsecase


class GetUserRolesUsecase(BaseUsecase):
    """Usecase для Получение ролей пользователя"""

    def get_user_roles(self, user_id: UUID) -> Dict[str, Any]:

        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            roles = [self._serialize_role(role) for role in user.roles]

            return self._handle_success(
                "Роли пользователя получены",
                data={
                    "user_id": str(user_id),
                    "roles": roles,
                    "total": len(roles)
                }
            )

        except Exception as e:
            return self._handle_error(e, "получения ролей пользователя")
