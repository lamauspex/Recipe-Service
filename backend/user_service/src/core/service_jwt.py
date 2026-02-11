""" Утилита для создания и верификации JWT токенов (без работы с БД) """


from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Dict, Optional


class JWTService:
    """Сервис для работы с JWT токенами (без доступа к БД)"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
        refresh_token_expire_days: int,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.encoder = jwt.algorithms.DefaultAlgorithm()

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
                minutes=self.access_token_expire_minutes
            )

        to_encode = payload.copy()
        to_encode.update({
            "exp": expire,
            "type": "access"
        })

        return jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

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
                days=self.refresh_token_expire_days
            )

        to_encode = payload.copy()
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })

        return jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

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
