from pydantic import BaseModel, field_validator

from backend.user_service.duble_service_dtoschemas.core.validator_password import PasswordValidator


class PasswordResetConfirm(BaseModel):
    """Схема для подтверждения сброса пароля"""

    token: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        validator = PasswordValidator()
        is_valid, errors = validator.validate_password(v)
        if not is_valid:
            raise ValueError('; '.join(errors))
        return v
