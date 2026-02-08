from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    user_name: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str
