"""
Логгер для сервисного слоя

Предоставляет удобный API для логирования вызовов методов сервисов
с автоматическим контекстом (имя сервиса, имя метода, параметры).
"""

import functools
from typing import Any, Callable, Optional, TypeVar, Union

from backend.shared.logging.logger import ContextLogger, get_logger

# Тип для Generic
F = TypeVar("F", bound=Callable[..., Any])


class ServiceLogger:
    """
    Логгер для сервисного слоя

    Использование:

    1. Внедрение через конструктор:

    ```python
    class MyService:
        def __init__(self, logger: ServiceLogger = None):
            self.logger = logger or ServiceLogger("MyService")
    ```

    2. Декоратор для методов:

    ```python
    @service_logger.log_call
    def my_method(self, arg1, arg2):
        return result
    ```
    """

    def __init__(
        self,
        service_name: str,
        logger: Optional[ContextLogger] = None,
        log_args: bool = True,
        log_result: bool = True,
    ):
        """
        Args:
            service_name: Имя сервиса (например, "AuthService")
            logger: Кастомный логгер (опционально)
            log_args: Логировать аргументы методов
            log_result: Логировать результат выполнения
        """
        self.service_name = service_name
        self.log_args = log_args
        self.log_result = log_result
        self._logger = logger or get_logger(__name__)

        # Базовый контекст для сервиса
        self._base_logger = self._logger.bind(
            layer="service",
            service=service_name,
        )

    def _bind_method(self, method_name: str) -> ContextLogger:
        """Создает логгер с контекстом метода"""
        return self._base_logger.bind(method=method_name)

    def log_call(
        self,
        func: Optional[F] = None,
        *,
        log_args: Optional[bool] = None,
        log_result: Optional[bool] = None,
    ) -> Union[Callable[[F], F], F]:
        """
        Декоратор для логирования вызова метода

        Args:
            log_args: Переопределить логирование аргументов
            log_result: Переопределить логирование результата

        Пример:
            @service_logger.log_call
            def do_something(self, arg1, arg2):
                return result
        """
        _log_args = log_args if log_args is not None else self.log_args
        _log_result = log_result if log_result is not None else self.log_result

        def decorator(fn: F) -> F:
            method_name = fn.__name__

            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                logger = self._bind_method(method_name)

                # Подготовка аргументов для логирования
                # Пропускаем self (первый аргумент)
                call_args = args[1:] if args else ()

                # Логируем вход
                log_data = {}
                if _log_args and call_args:
                    log_data["args"] = str(call_args)
                if _log_args and kwargs:
                    log_data["kwargs"] = str(kwargs)

                logger.info("→ Service call started", **log_data)

                # Выполняем метод
                try:
                    result = fn(*args, **kwargs)
                except Exception as exc:
                    # Логируем ошибку
                    logger.error(
                        "→ Service call failed",
                        error=type(exc).__name__,
                        message=str(exc),
                    )
                    raise

                # Логируем результат
                if _log_result:
                    logger.info(
                        "← Service call completed",
                        result=str(result)[:200],  # Ограничиваем вывод
                    )
                else:
                    logger.info("← Service call completed")

                return result

            return wrapper  # type: ignore

        # Поддержка вызова с аргументами и без
        if func is None:
            return decorator
        return decorator(func)

    def info(self, message: str, **kwargs: Any) -> None:
        """Логирование информационного сообщения"""
        self._base_logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Логирование отладочного сообщения"""
        self._base_logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Логирование предупреждения"""
        self._base_logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Логирование ошибки"""
        self._base_logger.error(message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Логирование исключения с трассировкой"""
        self._base_logger.exception(message, **kwargs)

    def bind(self, **kwargs: Any) -> "ServiceLogger":
        """Создает новый логгер с дополнительным контекстом"""
        new_logger = ServiceLogger(
            service_name=self.service_name,
            logger=self._logger,
            log_args=self.log_args,
            log_result=self.log_result,
        )
        new_logger._base_logger = self._base_logger.bind(**kwargs)
        return new_logger


# Утилита для быстрого создания логгера сервиса
def create_service_logger(service_name: str, **context) -> ServiceLogger:
    """Создает логгер для сервиса с дополнительным контекстом"""
    logger = ServiceLogger(service_name)
    if context:
        logger._base_logger = logger._base_logger.bind(**context)
    return logger
