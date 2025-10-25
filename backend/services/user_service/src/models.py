"""
Модели данных для user-service
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    username = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    email = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password = Column(
        String(255),
        nullable=False
    )
    full_name = Column(
        String(100),
        nullable=True
    )
    bio = Column(
        Text,
        nullable=True
    )
    is_active = Column(
        Boolean,
        default=True
    )
    is_admin = Column(
        Boolean,
        default=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    def __repr__(self):
        return (
            f"<User("
            f"id={self.id}, "
            f"username='{self.username}', "
            f"email='{self.email}'"
            f")>"
        )


class RefreshToken(Base):
    """Модель refresh token для JWT аутентификации"""
    __tablename__ = "refresh_tokens"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )
    user_id = Column(
        Integer,
        nullable=False
    )
    token = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    is_revoked = Column(
        Boolean,
        default=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"
