""" Утилита для создания и верификации JWT токенов (без работы с БД) """


from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Dict, Optional

from backend.user_service.src.config import settings


class JWTService:
    """Сервис для работы с JWT токенами (без доступа к БД)"""

    def __init__(
        self,
        secret_key: str = None,
        algorithm: str = None
    ):
        self.secret_key = secret_key or settings.SECRET_KEY
        self.algorithm = algorithm or settings.ALGORITHM

    def create_access_token(
        self,
        payload: Dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Создание access токена"""

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = payload.copy()
        to_encode.update({"exp": expire, "type": "access"})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(
        self,
        payload: Dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Создание refresh токена"""

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

        to_encode = payload.copy()
        to_encode.update({"exp": expire, "type": "refresh"})

        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[Dict]:
        """Декодирование токена"""

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            return None

    def verify_token_type(self, token: str, expected_type: str) -> bool:
        """Проверка типа токена"""

        payload = self.decode_token(token)
        if not payload:
            return False
        return payload.get("type") == expected_type
