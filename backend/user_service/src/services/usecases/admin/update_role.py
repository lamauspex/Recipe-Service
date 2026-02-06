

from ..base import BaseUsecase


class UpdateRoleUseCase(BaseUsecase):

    def update_role(self, role_id: UUID, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление роли"""
        try:
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not role:
                return ResponseBuilder.not_found("Роль")

            # Проверяем уникальность имени роли
            if "name" in update_data:
                existing_role = self.db_session.query(RoleModel).filter(
                    RoleModel.name == update_data["name"]
                ).first()

                if existing_role and existing_role.id != role_id:
                    return ResponseBuilder.error(
                        "Роль с таким именем уже существует",
                        error_code="ROLE_EXISTS"
                    )

            # Обновляем поля
            for field, value in update_data.items():
                if hasattr(role, field):
                    setattr(role, field, value)

            self.db_session.commit()

            return self._handle_success(
                "Роль обновлена",
                data=self._serialize_role(role)
            )

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "обновления роли")
