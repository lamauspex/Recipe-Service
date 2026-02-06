

from ..base import BaseUsecase
from backend.user_service.src.models.role_model import RoleModel
from backend.user_service.src.services.dto.requests import UserRoleRequestDTO
from backend.user_service.src.services.dto.responses import UserRoleResponseDTO


class CreateRoleUsecase(BaseUsecase):
    """ Usecase для для управления ролями """

    def __init__(
        self,
        user_repository,
        **kwargs
    ):
        self.user_repository = user_repository
        super().__init__(**kwargs)

    async def create_role(
        self,
        request: UserRoleRequestDTO
    ) -> UserRoleResponseDTO:
        """Создание новой роли"""

        try:
            # Проверяем, существует ли роль с таким именем
            existing_role = self.db_session.query(RoleModel).filter(
                RoleModel.name == role_data["name"]).first()

            if existing_role:
                return ResponseBuilder.error(
                    "Роль с таким именем уже существует",
                    error_code="ROLE_EXISTS"
                )

            # Создаем новую роль
            new_role = RoleModel(
                name=role_data["name"],
                description=role_data.get("description", ""),
                permissions=role_data.get("permissions", [])
            )

            self.db_session.add(new_role)
            self.db_session.commit()

            return self._handle_success(
                "Роль создана",
                data=self._serialize_role(new_role)
            )

        except Exception as e:
            self.db_session.rollback()
            return self._handle_error(e, "создания роли")
