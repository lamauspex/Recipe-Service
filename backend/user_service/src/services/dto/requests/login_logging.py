""" DTO для логирования входов """


from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoginAttemptLogRequestDTO(BaseModel):
    """DTO для логирования попытки входа"""

    email: str
    ip_address: str
    user_agent: Optional[str] = None
    success: bool = False
    failure_reason: Optional[str] = None
    timestamp: datetime = Field(
        default_factory=datetime.datetime
    )


class LoginHistoryRequestDTO(BaseModel):
    """DTO для запроса истории входов"""

    user_id: Optional[str] = None
    email: Optional[str] = None
    days: int = 7


class LoginStatisticsRequestDTO(BaseModel):
    """DTO для запроса статистики входов"""

    days: int = 7
