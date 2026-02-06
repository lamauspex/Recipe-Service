"""
Базовый класс для всех сервисов
Обеспечивает единообразную обработку ошибок и ответов
"""

import logging
from abc import ABC
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BaseService(ABC):
    """Базовый класс для всех сервисов"""

    def __init__(self):
        pass

    def _handle_error(self, error: Exception, operation: str, context: str = "") -> Dict[str, Any]:
        """Единообразная обработка ошибок"""

        error_msg = f"Ошибка {operation}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"

        logger.error(error_msg, exc_info=True)

        return {
            "error": error_msg,
            "success": False
        }

    def _handle_success(self, message: str, data: Any = None, **kwargs) -> Dict[str, Any]:
        """Единообразная обработка успешных операций"""

        result = {
            "message": message,
            "success": True
        }

        if data is not None:
            result["data"] = data

        # Добавляем дополнительные поля
        result.update(kwargs)

        return result
