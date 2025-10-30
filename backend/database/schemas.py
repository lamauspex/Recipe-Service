"""
Базовые схемы Pydantic для всех микросервисов
Содержит общие компоненты: UUID, временные метки, пагинация, базовые ответы
"""
from datetime import datetime
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# Тип для дженериков
T = TypeVar('T')


class UUIDMixin(BaseModel):
    """Миксин для UUID идентификатора"""
    id: UUID = Field(description="Уникальный идентификатор")


class TimestampMixin(BaseModel):
    """Миксин для временных меток"""
    created_at: datetime = Field(description="Время создания записи")
    updated_at: Optional[datetime] = Field(
        None,
        description="Время последнего обновления"
    )


class StatusMixin(BaseModel):
    """Миксин для статуса активности"""
    is_active: bool = Field(
        default=True,
        description="Флаг активности записи"
    )


class SoftDeleteMixin(BaseModel):
    """Миксин для мягкого удаления"""
    is_deleted: bool = Field(
        default=False,
        description="Флаг удаления"
    )
    deleted_at: Optional[datetime] = Field(
        None,
        description="Время удаления"
    )


class BaseResponse(UUIDMixin, TimestampMixin, StatusMixin):
    """Базовая схема ответа со всеми общими полями"""
    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Параметры пагинации"""
    skip: int = Field(
        default=0,
        ge=0,
        description="Количество пропущенных записей"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Количество записей на странице"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Схема пагинированного ответа"""
    items: List[T] = Field(description="Список элементов")
    total: int = Field(description="Общее количество элементов")
    skip: int = Field(description="Количество пропущенных элементов")
    limit: int = Field(description="Количество элементов на странице")
    has_more: bool = Field(description="Есть ли следующая страница")


class FilterParams(BaseModel):
    """Базовые параметры фильтрации"""
    search: Optional[str] = Field(
        None,
        description="Поисковая строка"
    )
    sort_by: Optional[str] = Field(
        None,
        description="Поле для сортировки"
    )
    sort_order: Optional[str] = Field(
        None,
        pattern="^(asc|desc)$",
        description="Порядок сортировки"
    )


class ErrorResponse(BaseModel):
    """Схема ответа с ошибкой"""
    error: str = Field(description="Текст ошибки")
    code: Optional[str] = Field(None, description="Код ошибки")
    details: Optional[Any] = Field(None, description="Дополнительные детали")


class SuccessResponse(BaseModel):
    """Схема успешного ответа"""
    message: str = Field(description="Сообщение об успехе")
    data: Optional[Any] = Field(None, description="Данные ответа")


class HealthCheckResponse(BaseModel):
    """Схема ответа проверки здоровья"""
    status: str = Field(description="Статус сервиса")
    timestamp: datetime = Field(description="Время проверки")
    service: str = Field(description="Название сервиса")
    version: str = Field(description="Версия сервиса")
    database: Optional[str] = Field(None, description="Статус базы данных")


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Имя пользователя"
    )
    email: str = Field(
        ...,
        description="Email пользователя"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Полное имя"
    )


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(
        ...,
        min_length=8,
        description="Пароль пользователя"
    )


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: Optional[str] = Field(None, description="Email пользователя")
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Полное имя"
    )
    bio: Optional[str] = Field(None, description="Биография")


class UserResponse(UserBase, BaseResponse):
    """Схема ответа с данными пользователя"""
    is_admin: bool = Field(description="Флаг администратора")
    bio: Optional[str] = Field(None, description="Биография пользователя")


class Token(BaseModel):
    """Схема токена доступа"""
    access_token: str = Field(description="Access токен")
    refresh_token: str = Field(description="Refresh токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: Optional[int] = Field(
        None, description="Время жизни токена в секундах")


class TokenData(BaseModel):
    """Схема данных из токена"""
    username: Optional[str] = Field(None, description="Имя пользователя")
    user_id: Optional[UUID] = Field(None, description="ID пользователя")
    is_admin: Optional[bool] = Field(None, description="Флаг администратора")


class Permission(BaseModel):
    """Схема прав доступа"""
    name: str = Field(description="Название права")
    description: Optional[str] = Field(None, description="Описание права")


class Role(BaseModel):
    """Схема роли пользователя"""
    name: str = Field(description="Название роли")
    description: Optional[str] = Field(None, description="Описание роли")
    permissions: List[Permission] = Field(
        default_factory=list, description="Список прав")


# Утилитные классы для валидации
class ValidationErrorDetail(BaseModel):
    """Детали ошибки валидации"""
    field: str = Field(description="Поле с ошибкой")
    message: str = Field(description="Сообщение об ошибке")
    value: Optional[Any] = Field(None, description="Некорректное значение")


class ValidationErrorResponse(ErrorResponse):
    """Схема ответа с ошибками валидации"""
    errors: List[ValidationErrorDetail] = Field(
        description="Список ошибок валидации")


# Дженерик для обертки данных
class DataWrapper(BaseModel, Generic[T]):
    """Обертка для данных с метаинформацией"""
    data: T = Field(description="Основные данные")
    meta: Optional[dict] = Field(None, description="Метаинформация")


# Экспортируемые константы для использования в других схемах
__all__ = [
    # Базовые миксины
    'UUIDMixin',
    'TimestampMixin',
    'StatusMixin',
    'SoftDeleteMixin',

    # Основные схемы
    'BaseResponse',
    'PaginationParams',
    'PaginatedResponse',
    'FilterParams',
    'ErrorResponse',
    'SuccessResponse',
    'HealthCheckResponse',

    # Пользовательские схемы
    'UserBase',
    'UserCreate',
    'UserUpdate',
    'UserResponse',

    # Аутентификация
    'Token',
    'TokenData',
    'Permission',
    'Role',

    # Валидация
    'ValidationErrorDetail',
    'ValidationErrorResponse',

    # Утилиты
    'DataWrapper'
]
