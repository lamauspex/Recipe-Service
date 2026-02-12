

from backend.user_service.src.schemas.base.base import PasswordValidatedModel


class PasswordResetConfirm(PasswordValidatedModel):
    """Схема для подтверждения сброса пароля"""

    token: str
