from pydantic import BaseModel


class LoginResponseDTO(BaseModel):
    """DTO ответа на вход пользователя с токенами"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
