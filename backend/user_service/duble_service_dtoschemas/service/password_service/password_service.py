"""
Служба для работы с паролями
"""

from passlib.context import CryptContext


class PasswordService:
    """ Класс для работы с паролями """

    def __init__(self):

        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto"
        )

    def verify_password(
        self,
        plain_password: str,
        hashed_password: str
    ) -> bool:
        """ Проверка пароля """

        return self.pwd_context.verify(
            plain_password,
            hashed_password
        )

    def hash_password(
        self,
        password: str
    ) -> str:
        """ Хэширование пароля """

        return self.pwd_context.hash(password)
