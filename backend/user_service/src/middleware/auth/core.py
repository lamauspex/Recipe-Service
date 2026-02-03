"""Базовые функции для авторизации"""


from fastapi import HTTPException, status

from user_service.models import User


async def get_current_user_core(user: User) -> User:
    """Базовая функция получения текущего пользователя"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация"
        )
    return user


def is_admin(user: User) -> bool:
    """Проверка, является ли пользователь администратором"""
    return user.role.is_admin() if user else False


def is_active(user: User) -> bool:
    """Проверка, является ли пользователь активным"""
    return user.is_active if user else False


def has_role(user: User, role_name: str) -> bool:
    """Проверка наличия определенной роли у пользователя"""
    if not user:
        return False
    return user.role.value.lower() == role_name.lower()


def validate_user_permissions(
    user: User,
    roles_service,
    permission: str
) -> bool:
    """Валидация наличия разрешения у пользователя"""
    if not user or not roles_service:
        return False
    return roles_service.user_has_permission(user.id, permission)
