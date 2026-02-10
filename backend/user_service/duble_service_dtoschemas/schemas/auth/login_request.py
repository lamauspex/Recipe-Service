from pydantic import BaseModel


class UserLogin(BaseModel):
    """Схема для входа пользователя"""

    user_name: str
    password: str
