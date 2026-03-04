""" Схемы для ответов """


from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Ответ с токенами"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
