"""
Базовые классы для usecase'ов
"""
from abc import ABC, abstractmethod
from typing import Any

from ..dto.requests import BaseRequestDTO
from ..dto.responses import BaseResponseDTO


class BaseUsecase(ABC):
    """Базовый класс для всех usecase'ов"""

    def __init__(self, **kwargs):
        self._validate_dependencies(**kwargs)

    def _validate_dependencies(self, **kwargs):
        """Проверка наличия всех необходимых зависимостей"""
        pass

    @abstractmethod
    async def execute(self, request: BaseRequestDTO) -> BaseResponseDTO:
        """Выполнение usecase'а"""
        pass


class UsecaseResult:
    """Класс для хранения результата выполнения usecase'а"""

    def __init__(
            self, success: bool = True, data: Any = None,
            message: str = "Success"):
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
            cls, data: Any = None,
            message: str = "Success") -> "UsecaseResult":
        """Создание успешного результата"""
        return cls(success=True, data=data, message=message)

    @classmethod
    def failure(
            cls, message: str = "Operation failed",
            errors: list = None) -> "UsecaseResult":
        """Создание неудачного результата"""
        result = cls(success=False, message=message)
        if errors:
            result.errors.extend(errors)
        return result
