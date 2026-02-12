""" Внутренний DTO для передачи данных между слоями приложения """

from pydantic import ConfigDict
from typing import Optional

from backend.user_service.src.schemas.base import (
    NameValidatedModel,
    EmailValidatedModel,
    HashedPasswordValidatedModel,
    FullNameValidatedModel,
    BooleanValidatedModel,
    DateTimeValidatedModel,
    RoleNameValidatedModel,
)
from backend.user_service.src.schemas.base.mixins import DTOConverterMixin


class UserRegistrationDTO(
    DTOConverterMixin,
    NameValidatedModel,
    EmailValidatedModel,
    HashedPasswordValidatedModel,
    FullNameValidatedModel,
    BooleanValidatedModel,
    DateTimeValidatedModel,
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
    - BooleanValidatedModel: валидация is_active, email_verified
    - DateTimeValidatedModel: валидация created_at, updated_at
    - RoleNameValidatedModel: валидация role_name
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        use_enum_values=True
    )

    # ========== Переопределение значений по умолчанию ==========
    email_verified: bool = False

    # ========== Методы для работы с DTO ==========

    def to_repository_dict(self) -> dict:
        """
        Переопределённый метод для UserRegistrationDTO.

        Автоматически исключает поля,
        которые не нужны для создания пользователя:
        - created_at, updated_at - устанавливаются на уровне БД
        - is_verified - поле из BooleanValidatedModel, не используемое в User

        Returns:
            dict: Словарь с данными для создания пользователя
        """
        return super().to_repository_dict(
            exclude={'created_at', 'updated_at', 'is_verified'}
        )

    # ========== Фабричные методы ==========

    @classmethod
    def from_user_create(
        cls,
        user_name: str,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        role_name: str = "user",
        is_active: bool = True,
        email_verified: bool = False
    ) -> "UserRegistrationDTO":
        """
        Создание DTO из базовых данных регистрации.

        Удобный фабричный метод для создания DTO после хеширования пароля.

        Args:
            user_name: Имя пользователя
            email: Email
            hashed_password: Хешированный пароль
            full_name: Полное имя (опционально)
            role_name: Имя роли (по умолчанию 'user')
            is_active: Активность пользователя (по умолчанию True)
            email_verified: Подтверждение email (по умолчанию False)

        Returns:
            UserRegistrationDTO: Созданный DTO
        """
        return cls(
            user_name=user_name,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role_name=role_name,
            is_active=is_active,
            email_verified=email_verified
        )
