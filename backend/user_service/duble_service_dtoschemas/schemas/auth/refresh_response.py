from pydantic import BaseModel


class RefreshResponseDTO(BaseModel):
    """DTO ответа на обновление токена"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
