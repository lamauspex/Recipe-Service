

from backend.service_user.src.schemas.base.base import PasswordValidatedModel


class PasswordResetConfirm(PasswordValidatedModel):
    """Схема для подтверждения сброса пароля"""

    token: str
