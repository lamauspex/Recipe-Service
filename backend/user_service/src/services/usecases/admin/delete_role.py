
from ..base import BaseUsecase


class DeleteRoleUsecase(BaseUsecase):
    """Usecase для Удаление роли"""

    def delete_role(self, role_id: UUID) -> Dict[str, Any]:

        try:
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not role:
                return ResponseBuilder.not_found("Роль")

            # Проверяем, есть ли пользователи с этой ролью
            users_with_role = self.db_session.query(User).filter(
                User.roles.any(RoleModel.id == role_id)
            ).count()

            if users_with_role > 0:
                return ResponseBuilder.error(
                    "Нельзя удалить роль, которая назначена пользователям",
                    error_code="ROLE_IN_USE"
                )

            self.db_session.delete(role)
            self.db_session.commit()

            return self._handle_success("Роль удалена")

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "удаления роли")
