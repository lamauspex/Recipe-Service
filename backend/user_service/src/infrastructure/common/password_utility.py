"""
Утилита для работы с паролями
Перенесено из старой архитектуры с улучшениями
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
        """Хеширование пароля с проверкой сложности"""
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        try:
            if not plain_password or not hashed_password:
                return False
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """Проверка, нужно ли перехешировать пароль"""
        try:
            return self.pwd_context.needs_update(hashed_password)
        except Exception:
            return True
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Проверка сложности пароля"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        return True, "Password is strong enough"


# Глобальный экземпляр для использования во всех сервисах
password_utility = PasswordUtility()
