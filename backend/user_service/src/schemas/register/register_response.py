from pydantic import BaseModel
from datetime import datetime
from typing import List


class UserResponseDTO(BaseModel):
    id: str
    user_name: str
    email: str
    full_name: str | None = None
    is_active: bool
    email_verified: bool
    roles: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
