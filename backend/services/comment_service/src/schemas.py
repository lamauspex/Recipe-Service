"""
Схемы Pydantic для comment-service
Наследуются от базовых схем из backend.database.schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID

from backend.database.schemas import (
    BaseResponse,
    PaginationParams,
    PaginatedResponse,
    SoftDeleteMixin
)


class CommentBase(BaseModel):
    """Базовая схема комментария"""
    content: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Текст комментария"
    )
    parent_id: Optional[UUID] = Field(
        None,
        description="ID родительского комментария"
    )


class CommentCreate(CommentBase):
    """Схема для создания комментария"""
    entity_id: UUID = Field(
        ...,
        description="ID сущности (рецепта, статьи и т.д.)"
    )
    entity_type: str = Field(
        ...,
        pattern="^(recipe|article|user)$",
        description="Тип сущности"
    )


class CommentUpdate(BaseModel):
    """Схема для обновления комментария"""
    content: Optional[str] = Field(
        None,
        min_length=1,
        max_length=2000
    )


class CommentResponse(CommentBase, BaseResponse, SoftDeleteMixin):
    """Схема ответа с данными комментария"""
    entity_id: UUID = Field(description="ID сущности")
    entity_type: str = Field(description="Тип сущности")
    author_id: UUID = Field(description="ID автора")
    like_count: int = Field(default=0, description="Количество лайков")
    reply_count: int = Field(default=0, description="Количество ответов")
    is_edited: bool = Field(
        default=False,
        description="Был ли комментарий отредактирован"
    )


class CommentTreeResponse(CommentResponse):
    """Схема комментария с древовидной структурой"""
    replies: List['CommentTreeResponse'] = Field(
        default_factory=list,
        description="Ответы на комментарий"
    )


class CommentSearchParams(PaginationParams):
    """Параметры поиска комментариев"""
    entity_id: Optional[UUID] = Field(
        None,
        description="Фильтр по ID сущности"
    )
    entity_type: Optional[str] = Field(
        None,
        pattern="^(recipe|article|user)$"
    )
    author_id: Optional[UUID] = Field(
        None,
        description="Фильтр по ID автора"
    )
    parent_id: Optional[UUID] = Field(
        None,
        description="Фильтр по родительскому комментарию"
    )
    include_replies: bool = Field(
        default=False,
        description="Включить ответы в результат"
    )


class CommentListResponse(PaginatedResponse[CommentResponse]):
    """Схема списка комментариев"""
    pass


class LikeBase(BaseModel):
    """Базовая схема лайка"""
    pass


class LikeCreate(BaseModel):
    """Схема для создания лайка"""
    comment_id: UUID = Field(
        ...,
        description="ID комментария"
    )


class LikeResponse(BaseResponse):
    """Схема ответа с данными лайка"""
    comment_id: UUID = Field(description="ID комментария")
    user_id: UUID = Field(description="ID пользователя")


class CommentStats(BaseModel):
    """Статистика комментариев"""
    entity_id: UUID = Field(description="ID сущности")
    entity_type: str = Field(description="Тип сущности")
    total_comments: int = Field(description="Общее количество комментариев")
    total_likes: int = Field(description="Общее количество лайков")
    average_rating: Optional[float] = Field(
        None,
        description="Средний рейтинг"
    )


class CommentModeration(BaseModel):
    """Схема для модерации комментариев"""
    is_approved: bool = Field(description="Одобрен ли комментарий")
    moderation_notes: Optional[str] = Field(
        None,
        description="Заметки модератора"
    )
    moderated_by: Optional[UUID] = Field(None, description="ID модератора")


# Дженерик схемы для использования в других сервисах
CommentPaginatedResponse = PaginatedResponse[CommentResponse]
CommentTreePaginatedResponse = PaginatedResponse[CommentTreeResponse]


__all__ = [
    'CommentBase',
    'CommentCreate',
    'CommentUpdate',
    'CommentResponse',
    'CommentTreeResponse',
    'CommentSearchParams',
    'CommentListResponse',
    'LikeBase',
    'LikeCreate',
    'LikeResponse',
    'CommentStats',
    'CommentModeration',
    'CommentPaginatedResponse',
    'CommentTreePaginatedResponse'
]
