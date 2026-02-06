
from ..base import BaseUsecase


class RemoveRoleFromUserUsecase(BaseUsecase):
    """Usecase для удаления роли у пользователя"""

    def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> Dict[str, Any]:

        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            if not role:
                return ResponseBuilder.not_found("Роль")

            if role not in user.roles:
                return ResponseBuilder.error(
                    "У пользователя нет этой роли",
                    error_code="ROLE_NOT_ASSIGNED"
                )

            user.remove_role(role)
            self.db_session.commit()

            return self._handle_success(
                f"Роль {role.name} удалена у пользователя"
            )

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "удаления роли")
