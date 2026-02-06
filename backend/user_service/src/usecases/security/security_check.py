"""
Usecase для комплексной проверки безопасности
"""

from uuid import UUID

from ...schemas.requests import BaseRequestDTO
from ...schemas.responses import BaseResponseDTO
from ..base import BaseUsecase
from ...infrastructure.common.exceptions import ValidationException


class SecurityCheckUsecase(BaseUsecase):
    """Usecase для комплексной проверки безопасности"""

    def __init__(self, user_repository, security_service, **kwargs):
        self.user_repository = user_repository
        self.security_service = security_service
        super().__init__(**kwargs)

    async def execute(self, request: BaseRequestDTO) -> BaseResponseDTO:
        """Выполнение комплексной проверки безопасности"""
        try:
            # Получение параметров из запроса
            email = getattr(request, 'email', None)
            ip_address = getattr(request, 'ip_address', None)
            user_agent = getattr(request, 'user_agent', None)
            user_id = getattr(request, 'user_id', None)

            # Валидация входных данных
            if not any([email, ip_address, user_id]):
                raise ValidationException(
                    "At least one identifier (email, IP, or user_id) must be provided")

            # Комплексная проверка безопасности
            security_result = await self.security_service.comprehensive_security_check(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )

            # Дополнительные проверки если указан user_id
            user_security_data = {}
            if user_id:
                try:
                    UUID(user_id)
                    user_security_data = await self._get_user_security_data(user_id)
                except ValueError:
                    pass

            # Формирование ответа
            response_data = {
                "security_check_result": security_result,
                "user_security_data": user_security_data,
                "timestamp": self._get_current_timestamp()
            }

            if security_result.get("checks_passed", False):
                return BaseResponseDTO(
                    success=True,
                    message="Security check passed",
                    data=response_data
                )
            else:
                return BaseResponseDTO(
                    success=False,
                    message="Security issues detected",
                    data=response_data
                )

        except Exception as e:
            if isinstance(e, ValidationException):
                raise e
            raise ValidationException(
                f"Failed to perform security check: {str(e)}")

    async def _get_user_security_data(self, user_id: str) -> dict:
        """Получение данных безопасности пользователя"""
        try:
            # Получение пользователя
            user = await self.user_repository.get_by_id(user_id)
            if not user:
                return {"error": "User not found"}

            # Подготовка данных безопасности
            security_data = {
                "user_id": user_id,
                "is_active": user.is_active,
                "is_locked": getattr(user, 'is_locked', False),
                "email_verified": getattr(user, 'email_verified', False),
                "last_login": getattr(user, 'last_login', None),
                "login_count": getattr(user, 'login_count', 0),
                "failed_login_attempts": getattr(user, 'failed_login_attempts', 0),
                "locked_until": getattr(user, 'locked_until', None),
                "lock_reason": getattr(user, 'lock_reason', None)
            }

            # Получение ролей пользователя
            user_roles = await self.user_repository.get_user_roles(user_id)
            security_data["roles"] = [
                self._serialize_role(role) for role in user_roles]

            # Получение разрешений пользователя
            user_permissions = await self.user_repository.get_user_permissions(user_id)
            security_data["permissions"] = user_permissions

            return security_data

        except Exception as e:
            return {"error": f"Failed to get user security data: {str(e)}"}

    def _serialize_role(self, role) -> dict:
        """Сериализация роли"""
        return {
            "id": str(role.id),
            "name": role.name,
            "display_name": role.display_name,
            "is_system": getattr(role, 'is_system', False),
            "is_active": getattr(role, 'is_active', True)
        }
