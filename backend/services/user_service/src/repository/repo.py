"""
Repository слой для работы с пользователями
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from backend.services.user_service.src.models import User, RefreshToken


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_data: dict) -> User:
        """Создание пользователя"""
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, update_data: dict) -> Optional[User]:
        """Обновление пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Удаление пользователя"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка пользователей"""
        return self.db.query(User).offset(skip).limit(limit).all()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получение списка активных пользователей"""
        return self.db.query(User).filter(
            User.is_active is True
        ).offset(skip).limit(limit).all()


class RefreshTokenRepository:
    """Репозиторий для работы с refresh токенами"""

    def __init__(self, db: Session):
        self.db = db

    def create_refresh_token(self, user_id: int, token: str, expires_at):
        """Создание refresh токена"""
        # Отзываем старые токены пользователя
        self.revoke_user_tokens(user_id)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token

    def get_valid_token(self, token: str) -> Optional[RefreshToken]:
        """Получение валидного токена"""
        return self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False
            )
        ).first()

    def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""
        refresh_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()

        if refresh_token:
            refresh_token.is_revoked = True
            self.db.commit()
            return True
        return False

    def revoke_user_tokens(self, user_id: int) -> None:
        """Отзыв всех токенов пользователя"""
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).update({"is_revoked": True})
        self.db.commit()

    def cleanup_expired_tokens(self) -> int:
        """Очистка просроченных токенов"""
        from datetime import datetime, timezone

        expired_count = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.now(timezone.utc)
        ).delete()

        self.db.commit()
        return expired_count


# Для обратной совместимости
class Repository(UserRepository):
    """Репозиторий для работы с пользователями (устаревшее название)"""
    pass
