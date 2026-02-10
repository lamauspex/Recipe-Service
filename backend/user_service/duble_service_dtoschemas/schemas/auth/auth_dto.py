from datetime import datetime
from pydantic import BaseModel


class AuthResultDTO(BaseModel):
    """DTO результата аутентификации"""

    user_id: int
    user_name: str
    role: str


class TokenPairDTO(BaseModel):
    """DTO пары токенов"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenDataDTO(BaseModel):
    """DTO данных для создания refresh токена"""

    user_id: int
    token: str
    expires_at: datetime
