
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Token(BaseModel):
    """Схема токена доступа"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    user_id: str
    user_name: str
    email: str
    email_verified: bool = False


class TokenData(BaseModel):
    """Схема данных из токена"""

    user_name: Optional[str] = None
    user_id: Optional[UUID] = None
    is_admin: bool = False


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена"""

    refresh_token: str
