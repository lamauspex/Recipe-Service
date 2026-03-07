""" Исключения для аутентификации """


class InvalidCredentialsException(Exception):
    """401 - Неверные учетные данные"""
    pass


class InvalidTokenException(Exception):
    """401 - Неверный или истёкший токен"""
    pass
