from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    """Схема для обновления токена"""

    refresh_token: str
