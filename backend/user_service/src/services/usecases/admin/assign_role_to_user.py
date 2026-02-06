
from ..base import BaseUsecase


class AssignRoleToUserUsecase(BaseUsecase):
    """Usecase для назначения роли пользователю"""

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> Dict[str, Any]:
        try:
            user = self.db_session.query(User).filter(
                User.id == user_id).first()
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not user:
                return ResponseBuilder.not_found("Пользователь")

            if not role:
                return ResponseBuilder.not_found("Роль")

            # Проверяем, есть ли уже эта роль у пользователя
            if role in user.roles:
                return ResponseBuilder.error(
                    "У пользователя уже есть эта роль",
                    error_code="ROLE_ALREADY_ASSIGNED"
                )

            user.add_role(role)
            self.db_session.commit()

            return self._handle_success(
                f"Роль {role.name} назначена пользователю"
            )

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "назначения роли")
