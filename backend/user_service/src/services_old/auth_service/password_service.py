"""
Сервис для работы с паролями
Теперь использует единую утилиту PasswordUtility
"""

from common.password_utility import password_utility


class PasswordService:
    """Класс для работы с паролями - обертка над PasswordUtility"""

    def __init__(self):
        # Используем глобальный экземпляр утилиты
        self.password_utility = password_utility

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return self.password_utility.verify_password(plain_password, hashed_password)

    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return self.password_utility.hash_password(password)

    def needs_rehash(self, hashed_password: str) -> bool:
        """Проверка, нужно ли перехешировать пароль"""
        return self.password_utility.needs_rehash(hashed_password)
