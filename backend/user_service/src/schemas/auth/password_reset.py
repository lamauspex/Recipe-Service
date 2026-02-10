

from backend.user_service.src.schemas.base import PasswordValidatedModel


class PasswordResetConfirm(PasswordValidatedModel):
    """Схема для подтверждения сброса пароля"""

    token: str
