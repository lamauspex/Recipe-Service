

from backend.service_user.src.schemas.base.base import PasswordValidatedModel


class UserLogin(PasswordValidatedModel):
    """Схема для входа пользователя"""

    user_name: str
