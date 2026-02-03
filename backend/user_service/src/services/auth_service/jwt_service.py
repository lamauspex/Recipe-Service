
"""
Служба для работы с JWT токенами
"""

from datetime import datetime, timezone, timedelta
from jose import jwt
from typing import Optional, Dict

from user_service.config import settings


class JWTService:
    """ Класс для работы с JWT токенами """

    def __init__(
        self,
        secret_key: str,
        algorithm: str,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def decode_token(self, token: str) -> Optional[Dict]:
        """  """

        payload = jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm]
        )
        return payload

    def create_access_token(
        self,
        data: Dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """  """

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        )
        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )

    def create_refresh_token(
        self,
        data: Dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """  """

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        )
        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
