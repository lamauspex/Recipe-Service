"""
Сервис аутентификации для user-service
Автономная реализация без зависимостей от общих модулей
"""


from backend.services.user_service.models.user_models import User
from backend.services.user_service.src.repository.token_repo import (
    RefreshTokenRepository
)
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets
import os
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from uuid import UUID
from dotenv import load_dotenv
load_dotenv()


# Настройки JWT из переменных окружения с значениями по умолчанию
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


class AuthService:
    """Сервис для работы с аутентификацией пользователей"""

    def __init__(self, db: Session):
        self.db = db
        self.refresh_token_repo = RefreshTokenRepository(db)
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """Проверка пароля"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля"""
        # Проверяем длину пароля в байтах
        if len(password.encode('utf-8')) > 1024:
            raise ValueError("Пароль слишком длинный (максимум 1024 байта)")

        return self.pwd_context.hash(password)

    def authenticate_user(
        self,
        user_name: str,
        password: str
    ) -> Optional[User]:
        """Аутентификация пользователя"""
        from .user_service import UserService
        user_service = UserService(self.db)
        user = user_service.get_user_by_username(user_name)

        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(
        self,
        data: dict,
        expires_delta:
        Optional[timedelta] = None
    ) -> str:
        """Создание access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        # Добавляем уникальный идентификатор для предотвращения коллизий
        to_encode.update({
            "exp": expire,
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # Уникальный ID токена
        })
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Создание refresh token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + \
                timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Добавляем уникальный идентификатор для предотвращения коллизий
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)  # Уникальный ID токена
        })
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_tokens(self, user: User) -> tuple[str, str]:
        """Создание access и refresh токенов для пользователя"""
        access_token_data = {"sub": user.user_name}
        refresh_token_data = {"sub": user.user_name, "user_id": str(user.id)}

        access_token = self.create_access_token(
            data=access_token_data,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = self.create_refresh_token(
            data=refresh_token_data,
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        # Сохранение refresh token в базу данных через репозиторий
        expires_at = datetime.now(timezone.utc) + \
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        self.refresh_token_repo.create_refresh_token(
            user.id, refresh_token, expires_at
        )

        return access_token, refresh_token

    def verify_token(self, token: str) -> Optional[dict]:
        """Верификация JWT токена"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_name: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_name is None or token_type is None:
                return None

            return payload
        except JWTError:
            return None

    def revoke_refresh_token(self, token: str) -> bool:
        """Отзыв refresh token"""
        return self.refresh_token_repo.revoke_token(token)

    def create_test_tokens(self) -> tuple[str, str]:
        """Метод для тестирования - создает тестовые токены"""
        # Для тестирования создаем токены для тестового пользователя с UUID
        test_uuid = UUID('12345678-1234-5678-1234-567812345678')
        access_token = self.create_access_token({"sub": "test_user"})
        refresh_token = self.create_refresh_token(
            {"sub": "test_user", "user_id": str(test_uuid)}
        )
        return access_token, refresh_token

    def get_user_from_token(self, token: str) -> Optional[User]:
        """Получение пользователя из токена"""
        payload = self.verify_token(token)
        if payload is None:
            return None

        user_name: str = payload.get("sub")
        if user_name is None:
            return None

        from .user_service import UserService
        user_service = UserService(self.db)
        return user_service.get_user_by_username(user_name)
