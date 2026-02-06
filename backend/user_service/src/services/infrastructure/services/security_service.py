"""
Адаптер для работы с безопасностью
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

from ...interfaces.security import SecurityInterface


class SecurityServiceAdapter(SecurityInterface):
    """Адаптер для работы с безопасностью"""

    def __init__(self, jwt_secret: str, jwt_algorithm: str = "HS256"):
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
        self.password_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto")

    async def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return self.password_context.hash(password)

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.password_context.verify(password, hashed_password)

    async def generate_access_token(self, user_data: Dict[str, Any]) -> str:
        """Генерация access токена"""
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode = {
            "exp": expire,
            "sub": str(user_data["user_id"]),
            "email": user_data["email"],
            "role": user_data["role"],
            "type": "access"
        }
        return jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)

    async def generate_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Генерация refresh токена"""
        expire = datetime.utcnow() + timedelta(days=30)
        to_encode = {
            "exp": expire,
            "sub": str(user_data["user_id"]),
            "email": user_data["email"],
            "role": user_data["role"],
            "type": "refresh"
        }
        return jwt.encode(
            to_encode,
            self.jwt_secret,
            algorithm=self.jwt_algorithm
        )

    async def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка access токена"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            if payload.get("type") != "access":
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None

    async def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Проверка refresh токена"""
        try:
            payload = jwt.decode(token, self.jwt_secret,
                                 algorithms=[self.jwt_algorithm])
            if payload.get("type") != "refresh":
                return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None

    async def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""
        # JWT токены нельзя отозвать напрямую,
        # но можно пометить как недействительные
        # в базе данных через refresh токены
        try:
            payload = jwt.decode(token, self.jwt_secret,
                                 algorithms=[self.jwt_algorithm])
            return payload.get("type") == "refresh"
        except jwt.JWTError:
            return False

    async def generate_password_reset_token(self, user_email: str) -> str:
        """Генерация токена для сброса пароля"""
        expire = datetime.utcnow() + timedelta(hours=1)
        to_encode = {
            "exp": expire,
            "sub": user_email,
            "type": "password_reset"
        }
        return jwt.encode(
            to_encode,
            self.jwt_secret,
            algorithm=self.jwt_algorithm
        )

    async def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Проверка токена для сброса пароля"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            if payload.get("type") != "password_reset":
                return None
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
