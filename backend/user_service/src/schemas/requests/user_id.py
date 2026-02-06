"""
DTO для запроса с ID пользователя
"""

from pydantic import BaseModel, Field
from uuid import UUID


class UserIdRequestDTO(BaseModel):
    """DTO для запроса с ID пользователя"""

    user_id: str = Field(..., description="ID пользователя (UUID)")

    def __init__(self, **data):
        # Конвертируем UUID в строку при инициализации
        if 'user_id' in data and isinstance(data['user_id'], UUID):
            data['user_id'] = str(data['user_id'])
        super().__init__(**data)

    class Config:
        schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
