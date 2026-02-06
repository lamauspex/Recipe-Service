
from backend.user_service.src.services.dto.responses import UserRoleResponseDTO
from ..base import BaseUsecase


class ListRolesUsecase(BaseUsecase):
    """Usecase для получения списка всех ролей"""

    def list_roles(self) -> UserRoleResponseDTO:
        """Получение списка всех ролей"""

        try:
            roles = self.db_session.query(RoleModel).all()

            return self._handle_success(
                "Список ролей получен",
                data={
                    "roles": [self._serialize_role(role) for role in roles],
                    "total": len(roles)
                }
            )

        except Exception as e:
            return self._handle_error(e, "получения списка ролей")
