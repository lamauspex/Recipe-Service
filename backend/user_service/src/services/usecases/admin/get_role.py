
from backend.user_service.src.services.dto.requests import UserRoleRequestDTO
from backend.user_service.src.services.dto.responses import UserRoleResponseDTO
from ..base import BaseUsecase


class GetRoleUsecase(BaseUsecase):
    def get_role(
        self,
        request: UserRoleRequestDTO
    ) -> UserRoleResponseDTO:
        """ "Usecase для получение роли по ID """

        try:
            role = self.db_session.query(RoleModel).filter(
                RoleModel.id == role_id).first()

            if not role:
                return ResponseBuilder.not_found("Роль")

            return self._handle_success(
                "Роль найдена",
                data=self._serialize_role(role)
            )

        except Exception as e:
            return self._handle_error(e, "получения роли")
