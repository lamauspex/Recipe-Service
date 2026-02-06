"""
JWT сервис для работы с токенами
Перенесено из старой архитектуры с улучшениями
"""

from datetime import datetime, timezone, timedelta
from jose import jwt
from typing import Optional, Dict, Any


class JWTService:
    """Класс для работы с JWT токенами"""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 30
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Декодирование токена"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
        except Exception:
            return None

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Создание access токена"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=self.access_token_expire_minutes)
        )
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
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Создание refresh токена"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(days=self.refresh_token_expire_days)
        )
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })

        return jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

    def is_token_expired(self, token: str) -> bool:
        """Проверка истечения токена"""
        payload = self.decode_token(token)
        if not payload:
            return True
        
        exp = payload.get("exp")
        if not exp:
            return True
        
        return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)

    def get_token_type(self, token: str) -> Optional[str]:
        """Получение типа токена"""
        payload = self.decode_token(token)
        return payload.get("type") if payload else None

    def extract_user_id(self, token: str) -> Optional[str]:
        """Извлечение ID пользователя из токена"""
        payload = self.decode_token(token)
        return payload.get("sub") if payload else None

    def validate_token_structure(self, token: str) -> bool:
        """Валидация структуры токена"""
        payload = self.decode_token(token)
        if not payload:
            return False
        
        required_fields = ["sub", "exp", "type"]
        return all(field in payload for field in required_fields)
