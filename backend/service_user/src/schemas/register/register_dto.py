""" Внутренний DTO для передачи данных между слоями приложения """

from pydantic import ConfigDict

from backend.service_user.src.schemas.base import (
    NameValidatedModel,
    EmailValidatedModel,
    HashedPasswordValidatedModel,
    RoleNameValidatedModel,
    UserStatusModel,
    UserTimestampsModel,
    FullNameValidatedModel
)
from backend.service_user.src.schemas.base.mixins import DTOConverterMixin


class UserRegistrationDTO(
    DTOConverterMixin,
    NameValidatedModel,
    EmailValidatedModel,
    HashedPasswordValidatedModel,
    FullNameValidatedModel,
    UserStatusModel,
    UserTimestampsModel,
    RoleNameValidatedModel
):
    """
    Внутренний DTO для создания пользователя.

    Используется для передачи данных от API-слоя к репозиторию.
    Содержит хешированный пароль и служебные поля.

    Наследует валидацию от базовых схем:
    - NameValidatedModel: валидация user_name
    - EmailValidatedModel: валидация и нормализация email
    - HashedPasswordValidatedModel: проверка хешированного пароля
    - FullNameValidatedModel: валидация и нормализация full_name
    - UserStatusModel: валидация is_active, email_verified
    - UserTimestampsModel: валидация created_at, updated_at
    - RoleNameValidatedModel: валидация role_name
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        use_enum_values=True
    )

    # ========== Методы для работы с DTO ==========

    def to_repository_dict(self) -> dict:
        """
        Переопределённый метод для UserRegistrationDTO.

        Исключает поля, которые устанавливаются на уровне БД:
        - created_at, updated_at

        Returns:
            dict: Словарь с данными для создания пользователя
        """
        return super().to_repository_dict(
            exclude={'created_at', 'updated_at'}
        )
