"""
Usecase для проверки лимитов запросов
"""

from uuid import UUID

from ...schemas.requests import BaseRequestDTO
from ...schemas.responses import BaseResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException


class RateLimitCheckUsecase(BaseUsecase):
    """Usecase для проверки лимитов запросов"""

    def __init__(self, user_repository, security_service, **kwargs):
        self.user_repository = user_repository
        self.security_service = security_service
        super().__init__(**kwargs)

    async def execute(self, request: BaseRequestDTO) -> BaseResponseDTO:
        """Выполнение проверки лимитов запросов"""
        try:
            # Получение параметров из запроса
            email = getattr(request, 'email', None)
            ip_address = getattr(request, 'ip_address', None)

            if not email and not ip_address:
                raise ValidationException(
                    "Either email or IP address must be provided")

            # Проверка лимитов
            is_allowed, message = await self.security_service.check_rate_limit(
                email=email,
                ip_address=ip_address
            )

            if not is_allowed:
                return BaseResponseDTO(
                    success=False,
                    message=message or "Rate limit exceeded"
                )

            # Получение информации о лимитах
            limit_info = await self.security_service.rate_limit_utility.get_limit_info(
                email=email,
                ip_address=ip_address
            ) if self.security_service.rate_limit_utility else {}

            # Возврат результата
            return BaseResponseDTO(
                success=True,
                message="Rate limit check passed",
                data={
                    "rate_limit_ok": is_allowed,
                    "limit_info": limit_info,
                    "timestamp": self._get_current_timestamp()
                }
            )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise e
            raise ValidationException(f"Failed to check rate limit: {str(e)}")
