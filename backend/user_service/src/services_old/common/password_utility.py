"""
Единая утилита для работы с паролями
Устраняет дублирование кода хеширования и проверки паролей
"""

from passlib.context import CryptContext
from typing import Tuple


class PasswordUtility:
    """Единая утилита для работы с паролями"""
    
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["argon2"],
            deprecated="auto"
        )
    
    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """Проверка, нужно ли перехешировать пароль"""
        try:
            return self.pwd_context.needs_update(hashed_password)
        except Exception:
            return True


# Глобальный экземпляр для использования во всех сервисах
password_utility = PasswordUtility()