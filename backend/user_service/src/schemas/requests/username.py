"""
DTO для запроса пользователя по username
"""

from pydantic import BaseModel, Field


class UsernameRequestDTO(BaseModel):
    """DTO для запроса пользователя по username"""

    username: str = Field(..., min_length=3, max_length=50,
                          description="Username пользователя")

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe"
            }
        }
