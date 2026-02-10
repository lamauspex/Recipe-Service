from pydantic import EmailStr
from typing import Optional

from backend.user_service.src.schemas import (
    PasswordValidatedModel,
    NameValidatedModel
)


class UserCreate(PasswordValidatedModel, NameValidatedModel):
    """Схема для регистрации пользователя"""

    email: EmailStr
    full_name: Optional[str] = None
