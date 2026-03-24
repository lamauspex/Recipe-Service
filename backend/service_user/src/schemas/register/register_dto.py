""" Внутренний DTO для регистрации пользователя """

from pydantic import ConfigDict

from backend.service_user.src.schemas.base import (
    NameValidatedModel,
    EmailValidatedModel,
    HashedPasswordValidatedModel,
    RoleNameValidatedModel,
    UserStatusModel,
    FullNameValidatedModel,
    DTOConverterMixin
)


class UserRegistrationDTO(
    DTOConverterMixin,
    NameValidatedModel,
    EmailValidatedModel,
    HashedPasswordValidatedModel,
    FullNameValidatedModel,
    UserStatusModel,
    RoleNameValidatedModel
):
    """
    DTO для создания пользователя (сервисный слой)

    Используется для передачи данных от API-слоя к репозиторию.
    Содержит хешированный пароль и служебные поля.

    Наследует валидацию от базовых схем:
    - NameValidatedModel: валидация user_name
    - EmailValidatedModel: валидация email
    - HashedPasswordValidatedModel: проверка хешированного пароля
    - FullNameValidatedModel: валидация full_name
    - UserStatusModel: валидация is_active, email_verified
    - UserTimestampsModel: валидация timestamps
    - RoleNameValidatedModel: валидация role_name

    Attributes:
        user_name: Имя пользователя
        email: Email пользователя
        hashed_password: Хешированный пароль
        full_name: Полное имя
        is_active: Статус активности
        email_verified: Статус верификации email
        created_at: Время создания
        updated_at: Время обновления
        role_name: Роль пользователя

    Example:
        >>> dto = UserRegistrationDTO(
        ...     user_name="john_doe",
        ...     email="john@example.com",
        ...     hashed_password="$2b$12$...",
        ...     full_name="John Doe"
        ... )
    """

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "user_name": "john_doe",
                "email": "john@example.com",
                "hashed_password": "$2b$12$ hashed_password",
                "full_name": "John Doe",
                "is_active": True,
                "email_verified": False,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "role_name": "user"
            }
        }
    )

    # ========== Методы для работы с DTO ==========

    def to_repository_dict(self) -> dict:
        """
        Преобразование в словарь для репозитория.

        Исключает служебные поля, которые устанавливаются БД:
        - created_at
        - updated_at

        Returns:
            dict: Словарь для создания записи в БД
        """
        return super().to_repository_dict(
            exclude={
                'created_at',
                'updated_at'
            }
        )
