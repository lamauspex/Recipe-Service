from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class UserRegistrationDTO(BaseModel):
    # def __init__(
    #     self,
    #     user_name: str,
    #     email: str,
    #     full_name: str | None,
    #     hashed_password: str,
    #     is_active: bool = True,
    #     email_verified: bool = False,
    #     created_at: datetime | None = None,
    #     updated_at: datetime | None = None
    # ):
    #     self.user_name = user_name
    #     self.email = email
    #     self.full_name = full_name
    #     self.hashed_password = hashed_password
    #     self.is_active = is_active
    #     self.email_verified = email_verified
    #     self.created_at = created_at or datetime.now(timezone.utc)
    #     self.updated_at = updated_at or datetime.now(timezone.utc)

    # def to_dict(self) -> dict:
    #     return {
    #         "user_name": self.user_name,
    #         "email": self.email,
    #         "full_name": self.full_name,
    #         "hashed_password": self.hashed_password,
    #         "is_active": self.is_active,
    #         "email_verified": self.email_verified,
    #         "created_at": self.created_at,
    #         "updated_at": self.updated_at
    #     }

    user_name: str
    email: str
    full_name: Optional[str] = None
    hashed_password: str
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
