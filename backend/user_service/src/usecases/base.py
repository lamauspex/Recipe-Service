"""
Базовые классы для usecase'ов
"""

from typing import Any, Dict
from abc import ABC, abstractmethod
from datetime import datetime

from ..schemas.requests import BaseRequestDTO
from ..schemas.responses import BaseResponseDTO


class BaseUsecase(ABC):
    """Базовый класс для всех usecase'ов"""

    def __init__(self, **kwargs):
        self._validate_dependencies(**kwargs)

    def _validate_dependencies(self, **kwargs):
        """Проверка наличия всех необходимых зависимостей"""
        pass

    @abstractmethod
    async def execute(
        self,
        request: BaseRequestDTO
    ) -> BaseResponseDTO:
        """Выполнение usecase'а"""
        pass

    # === Методы из старого BaseService ===

    def _handle_success(self, message: str = "Success", data: Any = None, **kwargs) -> BaseResponseDTO:
        """Создание успешного ответа"""
        response = BaseResponseDTO()
        response.success = True
        response.message = message
        response.data = data or {}
        response.data.update(kwargs)
        return response

    def _handle_error(self, error: Exception, operation: str = "operation", context: str = "") -> BaseResponseDTO:
        """Создание ответа с ошибкой"""
        error_msg = f"Error {operation}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"

        response = BaseResponseDTO()
        response.success = False
        response.message = error_msg
        return response

    # === Методы сериализации ===

    def _serialize_role(self, role) -> Dict[str, Any]:
        """Сериализация роли"""
        return {
            "id": str(role.id),
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "permissions": role.permissions,
            "permissions_list": [p.name for p in role.permissions_list],
            "is_system": role.is_system,
            "is_active": role.is_active,
            "created_at": role.created_at.isoformat() if role.created_at else None,
            "updated_at": role.updated_at.isoformat() if role.updated_at else None
        }

    def _serialize_user(self, user) -> Dict[str, Any]:
        """Сериализация пользователя"""
        return {
            "id": str(user.id),
            "user_name": user.user_name,
            "email": user.email,
            "full_name": user.full_name,
            "bio": user.bio,
            "email_verified": user.email_verified,
            "is_active": user.is_active,
            "is_locked": user.is_locked,
            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
            "lock_reason": user.lock_reason,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "login_count": user.login_count,
            "roles": [self._serialize_role(role) for role in user.roles],
            "primary_role": self._serialize_role(user.primary_role) if user.primary_role else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }

    # === Дополнительные утилиты ===

    def _validate_uuid(self, uuid_str: str) -> bool:
        """Валидация UUID строки"""
        try:
            from uuid import UUID
            UUID(uuid_str)
            return True
        except (ValueError, TypeError):
            return False

    def _get_current_timestamp(self) -> str:
        """Получение текущего времени в ISO формате"""
        return datetime.utcnow().isoformat()

    def _format_pagination(self, items: list, total: int, page: int, per_page: int) -> Dict[str, Any]:
        """Форматирование пагинации"""
        total_pages = (total + per_page - 1) // per_page

        return {
            "items": items,
            "pagination": {
                "current_page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }


class UsecaseResult:
    """Класс для хранения результата выполнения usecase'а"""

    def __init__(
            self,
            success: bool = True,
            data: Any = None,
            message: str = "Success"
    ):
        self.success = success
        self.data = data
        self.message = message
        self.errors = []

    def add_error(self, error: str):
        """Добавление ошибки"""
        self.errors.append(error)
        self.success = False
        return self

    @classmethod
    def success(
            cls,
            data: Any = None,
            message: str = "Success"
    ) -> "UsecaseResult":
        """Создание успешного результата"""
        return cls(
            success=True,
            data=data,
            message=message
        )

    @classmethod
    def failure(
            cls,
            message: str = "Operation failed",
            errors: list = None
    ) -> "UsecaseResult":
        """Создание неудачного результата"""
        result = cls(
            success=False,
            message=message
        )
        if errors:
            result.errors.extend(errors)
        return result


class ResponseBuilder:
    """Утилита для создания стандартных ответов"""

    @staticmethod
    def success(data: Any = None, message: str = "Success") -> Dict[str, Any]:
        return {
            "success": True,
            "data": data,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def error(message: str, error_code: str = None, details: Dict[str, Any] = None) -> Dict[str, Any]:
        response = {
            "success": False,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        if error_code:
            response["error_code"] = error_code
        if details:
            response["details"] = details
        return response

    @staticmethod
    def paginated_response(items: list, total: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Создание ответа с пагинацией"""
        total_pages = (total + per_page - 1) // per_page

        return {
            "success": True,
            "data": {
                "items": items,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    def validation_error(field_errors: Dict[str, list]) -> Dict[str, Any]:
        return ResponseBuilder.error(
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details={"field_errors": field_errors}
        )

    @staticmethod
    def not_found(resource: str = "Resource") -> Dict[str, Any]:
        return ResponseBuilder.error(
            f"{resource} not found",
            "RESOURCE_NOT_FOUND"
        )

    @staticmethod
    def unauthorized(message: str = "Unauthorized access") -> Dict[str, Any]:
        return ResponseBuilder.error(
            message,
            "UNAUTHORIZED"
        )

    @staticmethod
    def forbidden(message: str = "Access forbidden") -> Dict[str, Any]:
        return ResponseBuilder.error(
            message,
            "FORBIDDEN"
        )

    @staticmethod
    def conflict(message: str = "Conflict occurred") -> Dict[str, Any]:
        return ResponseBuilder.error(
            message,
            "CONFLICT"
        )
