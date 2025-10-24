"""
Сервис аутентификации для user-service
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib import CryptContext
from sqlalchemy.orm import Session

from backend.services.user_service.src.models import User, RefreshToken

# Настройки JWT
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Сервис для работы с аутентификацией пользователей"""

    def __init__(self, db: Session):
        self.db = db

    def verify_password(self,
                        plain_password: str,
                        hashed_password: str
                        ) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)

    def authenticate_user(self,
                          username: str,
                          password: str
                          ) -> Optional[User]:
        """Аутентификация пользователя"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self,
                            data: dict,
                            expires_delta:
                                Optional[timedelta] = None
                            ) -> str:
        """Создание access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self,
                             data: dict,
                             expires_delta: Optional[timedelta] = None
                             ) -> str:
        """Создание refresh token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_tokens(self, user: User) -> tuple[str, str]:
        """Создание access и refresh токенов для пользователя"""
        access_token_data = {"sub": user.username}
        refresh_token_data = {"sub": user.username, "user_id": user.id}

        access_token = self.create_access_token(
            data=access_token_data,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = self.create_refresh_token(
            data=refresh_token_data,
            expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )

        # Сохранение refresh token в базу данных
        self._save_refresh_token(user.id, refresh_token)

        return access_token, refresh_token

    def _save_refresh_token(self, user_id: int, token: str) -> None:
        """Сохранение refresh token в базу данных"""
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Проверяем, есть ли уже токен для этого пользователя
        existing_token = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).first()

        if existing_token:
            # Обновляем существующий токен
            existing_token.token = token
            existing_token.expires_at = expires_at
            existing_token.is_revoked = False
        else:
            # Создаем новый токен
            refresh_token = RefreshToken(
                user_id=user_id,
                token=token,
                expires_at=expires_at
            )
            self.db.add(refresh_token)

        self.db.commit()

    def verify_token(self, token: str) -> Optional[dict]:
        """Верификация JWT токена"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            token_type: str = payload.get("type")

            if username is None or token_type is None:
                return None

            return payload
        except JWTError:
            return None

    def revoke_refresh_token(self, token: str) -> bool:
        """Отзыв refresh token"""
        refresh_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()

        if refresh_token:
            refresh_token.is_revoked = True
            self.db.commit()
            return True

        return False

    def create_test_tokens(self) -> tuple[str, str]:
        """Метод для тестирования - создает тестовые токены"""
        # Для тестирования создаем токены для тестового пользователя
        access_token = self.create_access_token({"sub": "test_user"})
        refresh_token = self.create_refresh_token(
            {"sub": "test_user", "user_id": 1})
        return access_token, refresh_token
