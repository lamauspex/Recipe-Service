"""
Логирование бизнес-событий, действий пользователей и аудита
"""


from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from user_service.config import settings
from user_service.middleware.logging.utils_trace_id import get_trace_id
from user_service.middleware.logging.loggers import (
    business_logger,
    security_logger,
)


class BusinessEventLogger:
    """
    Логгер для бизнес-событий и действий пользователей
    """

    @staticmethod
    def log_user_action(
        user_id: str,
        action: str,
        details: Optional[dict[str, Any]] = None,
        success: bool = True,
        resource: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> None:
        """
        Логирует действие пользователя

        Args:
            user_id: ID пользователя
            action: Тип действия (login, logout, create_user, etc.)
            details: Дополнительные детали действия
            success: Успешность действия
            resource: Затронутый ресурс
            metadata: Метаданные для аналитики
            trace_id: Trace ID (берётся из контекста если не передан)
        """
        # Проверяем, включено ли бизнес-логирование
        if not settings.monitoring.ENABLE_BUSINESS_LOGGING:
            return

        business_logger.info(
            "user_action",
            trace_id=trace_id or get_trace_id(),
            timestamp=datetime.utcnow().isoformat(),
            event_type="user_action",
            user_id=user_id,
            action=action,
            success=success,
            resource=resource,
            details=details or {},
            metadata=metadata or {},
        )

    @staticmethod
    def log_auth_event(
        username: str,
        success: bool,
        details: Optional[dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> None:
        """
        Логирует событие аутентификации

        Args:
            username: Имя пользователя
            success: Успешность аутентификации
            details: Дополнительные детали
            user_id: ID пользователя
            ip_address: IP адрес клиента
            user_agent: User-Agent клиента
            failure_reason: Причина неудачи
            trace_id: Trace ID
        """
        # Проверяем, включено ли бизнес-логирование
        if not settings.monitoring.ENABLE_BUSINESS_LOGGING:
            return

        log_data = {
            "trace_id": trace_id or get_trace_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "auth",
            "username": username,
            "success": success,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
        }

        if not success and failure_reason:
            log_data["failure_reason"] = failure_reason

        business_logger.info("authentication_event", **log_data)

    @staticmethod
    def log_admin_action(
        admin_id: str,
        action: str,
        target: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        success: bool = True,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> None:
        """
        Логирует административное действие

        Args:
            admin_id: ID администратора
            action: Тип действия
            target: Цель действия
            details: Дополнительные детали
            success: Успешность действия
            resource_type: Тип ресурса
            resource_id: ID ресурса
            metadata: Метаданные для аудита
            trace_id: Trace ID
        """
        # Проверяем, включено ли бизнес-логирование
        if not settings.monitoring.ENABLE_BUSINESS_LOGGING:
            return

        business_logger.info(
            "admin_action",
            trace_id=trace_id or get_trace_id(),
            timestamp=datetime.utcnow().isoformat(),
            event_type="admin_action",
            admin_id=admin_id,
            action=action,
            target=target,
            success=success,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            metadata=metadata or {},
        )

    @staticmethod
    def log_security_event(
        event_type: str,
        description: str,
        severity: str = "INFO",
        details: Optional[dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        blocked: bool = False,
        trace_id: Optional[str] = None
    ) -> None:
        """
        Логирует событие безопасности

        Args:
            event_type: Тип события
            description: Описание события
            severity: Уровень серьезности (INFO, WARNING, ERROR, CRITICAL)
            details: Дополнительные детали
            user_id: ID пользователя
            ip_address: IP адрес
            user_agent: User-Agent
            blocked: Был ли заблокирован доступ
            trace_id: Trace ID
        """
        # Проверяем, включено ли бизнес-логирование
        if not settings.monitoring.ENABLE_BUSINESS_LOGGING:
            return

        log_data = {
            "trace_id": trace_id or get_trace_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "security",
            "security_event_type": event_type,
            "description": description,
            "severity": severity,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "blocked": blocked,
            "details": details or {},
        }

        log_method = {
            "CRITICAL": security_logger.critical,
            "ERROR": security_logger.error,
            "WARNING": security_logger.warning,
            "INFO": security_logger.info,
        }.get(severity, security_logger.info)

        log_method("security_event", **log_data)

    @staticmethod
    def log_api_event(
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        user_id: Optional[str] = None,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> None:
        """
        Логирует API событие для аналитики

        Args:
            endpoint: Путь API эндпоинта
            method: HTTP метод
            status_code: Код ответа
            response_time_ms: Время ответа в мс
            user_id: ID пользователя
            request_size: Размер запроса в байтах
            response_size: Размер ответа в байтах
            details: Дополнительные детали
            trace_id: Trace ID
        """
        # Проверяем, включено ли бизнес-логирование
        if not settings.monitoring.ENABLE_BUSINESS_LOGGING:
            return

        business_logger.info(
            "api_event",
            trace_id=trace_id or get_trace_id(),
            timestamp=datetime.utcnow().isoformat(),
            event_type="api",
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=round(response_time_ms, 2),
            user_id=user_id,
            request_size=request_size,
            response_size=response_size,
            details=details or {},
        )

    @staticmethod
    def log_business_metric(
        metric_name: str,
        value: float,
        unit: str = "count",
        tags: Optional[dict[str, str]] = None,
        timestamp: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> None:
        """
        Логирует бизнес-метрику

        Args:
            metric_name: Название метрики
            value: Значение метрики
            unit: Единица измерения
            tags: Теги для группировки
            timestamp: Временная метка
            trace_id: Trace ID
        """
        # Проверяем, включено ли бизнес-логирование
        if not settings.monitoring.ENABLE_BUSINESS_LOGGING:
            return

        business_logger.info(
            "business_metric",
            trace_id=trace_id or get_trace_id(),
            timestamp=timestamp or datetime.utcnow().isoformat(),
            event_type="metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags or {},
        )
