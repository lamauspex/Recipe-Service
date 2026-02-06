
from backend.user_service.src.services.dto.responses import BaseResponseDTO

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class LoginHistoryItemDTO(BaseModel):
    """Элемент истории входа пользователя"""
    timestamp: datetime
    ip_address: str
    user_agent: Optional[str] = None
    success: bool = False
    failure_reason: Optional[str] = None


class LoginAttemptLogResponseDTO(BaseResponseDTO):
    data: Dict[str, Any] = {}

    @classmethod
    def create_success(cls, log_data: Dict[str, Any]):
        return cls(
            message="Попытка входа залогирована",
            data=log_data
        )


class LoginHistoryResponseDTO(BaseResponseDTO):
    data: Dict[str, Any] = {}

    @classmethod
    def create_success(
        cls,
        user_id: str,
        email: str,
        period_days: int,
        history: List[LoginHistoryItemDTO],
        account_created: datetime,
        note: Optional[str] = None
    ):
        return cls(
            message="История входов получена",
            data={
                "user_id": user_id,
                "email": email,
                "period_days": period_days,
                "history": [item.dict() for item in history],
                "account_created": account_created.isoformat(),
                "note": note
            })


class LoginStatisticsResponseDTO(BaseResponseDTO):
    data: Dict[str, Any] = {}

    @classmethod
    def create_success(
        cls,
        period_days: int,
        users_with_logins: int,
        users_today: int,
        top_ips: List,
        generated_at: datetime
    ):
        return cls(
            message="Статистика входов получена",
            data={
                "period_days": period_days,
                "users_with_logins": users_with_logins,
                "users_today": users_today,
                "top_ips": top_ips,
                "generated_at": generated_at.isoformat()
            })


class FailedLoginAttemptItemDTO(BaseModel):
    """Элемент неудачной попытки входа"""

    timestamp: datetime
    email: str
    ip_address: str
    user_agent: Optional[str] = None
    failure_reason: str


class FailedLoginAttemptsResponseDTO(BaseResponseDTO):
    """DTO для ответа неудачных попыток входа"""

    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(
        cls,
        period_days: int,
        failed_attempts: List[Dict[str, Any]],
        note: str = None
    ) -> "FailedLoginAttemptsResponseDTO":
        return cls(
            message="Неудачные попытки входа получены",
            data={
                "period_days": period_days,
                "failed_attempts": failed_attempts,
                "total_count": len(failed_attempts),
                "note": note or "Требуется отдельная таблица логов для детальной информации"
            }
        )
