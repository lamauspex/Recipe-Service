"""
Утилита для создания единообразных API ответов
Устраняет дублирование паттернов ответов
"""

from typing import Any, Dict, Optional, List
from datetime import datetime


class ResponseBuilder:
    """Утилита для создания единообразных API ответов"""
    
    @staticmethod
    def success(message: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Создание успешного ответа"""
        result = {
            "message": message,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        if data is not None:
            result["data"] = data
            
        # Добавляем дополнительные поля
        result.update(kwargs)
        return result
    
    @staticmethod
    def error(message: str, error_code: str = None, details: Any = None, **kwargs) -> Dict[str, Any]:
        """Создание ответа с ошибкой"""
        result = {
            "error": message,
            "success": False,
            "timestamp": datetime.now().isoformat()
        }
        
        if error_code:
            result["error_code"] = error_code
            
        if details:
            result["details"] = details
            
        # Добавляем дополнительные поля
        result.update(kwargs)
        return result
    
    @staticmethod
    def paginated_response(items: List[Any], total: int, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
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
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def validation_error(field_errors: Dict[str, List[str]]) -> Dict[str, Any]:
        """Создание ответа с ошибками валидации"""
        return ResponseBuilder.error(
            message="Ошибка валидации данных",
            error_code="VALIDATION_ERROR",
            details={"field_errors": field_errors}
        )
    
    @staticmethod
    def not_found(resource: str = "Ресурс") -> Dict[str, Any]:
        """Создание ответа для не найденного ресурса"""
        return ResponseBuilder.error(
            message=f"{resource} не найден",
            error_code="NOT_FOUND"
        )
    
    @staticmethod
    def unauthorized(message: str = "Неавторизованный доступ") -> Dict[str, Any]:
        """Создание ответа для неавторизованного доступа"""
        return ResponseBuilder.error(
            message=message,
            error_code="UNAUTHORIZED"
        )
    
    @staticmethod
    def forbidden(message: str = "Доступ запрещен") -> Dict[str, Any]:
        """Создание ответа для запрещенного доступа"""
        return ResponseBuilder.error(
            message=message,
            error_code="FORBIDDEN"
        )