""" Исключения аутентификации """

from .base import AppException


class InvalidCredentialsException(AppException):
    """401 - Неверные учетные данные"""

    def __init__(
        self,
        message: str = "Неверные учетные данные"
    ):
        super().__init__(
            message=message,
            status_code=401,
            code="INVALID_CREDENTIALS"
        )


class InvalidTokenException(AppException):
    """401 - Неверный токен"""

    def __init__(
        self,
        message: str = "Неверный токен"
    ):
        super().__init__(
            message=message,
            status_code=401,
            code="INVALID_TOKEN"
        )


class TokenExpiredException(AppException):
    """401 - Токен истёк"""

    def __init__(
        self,
        message: str = "Токен истёк"
    ):
        super().__init__(
            message=message,
            status_code=401,
            code="TOKEN_EXPIRED"
        )
