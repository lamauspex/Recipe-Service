

from pydantic import (
    BaseModel,
    EmailStr
)
from typing import Optional


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    user_name: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""

    password: str
