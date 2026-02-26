"""
Перечисления и константы — независимый слой (не импортирует ничего!)
"""


from enum import IntFlag
from dataclasses import dataclass


class Permission(IntFlag):
    """Разрешения системы (битовая маска)"""

    NONE = 0
    READ = 1
    WRITE = 2
    DELETE = 4
    MANAGE_USERS = 8
    MANAGE_ROLES = 16
    VIEW_STATS = 32
    SYSTEM_CONFIG = 64
    BAN_USERS = 128
    FULL_ACCESS = 255


@dataclass(frozen=True)
class Role:
    """Статическое описание роли (не хранится в БД)"""

    name: str
    display_name: str
    description: str
    permissions: Permission
    is_system: bool


# Предопределённые роли
ROLES: dict[str, Role] = {

    "user": Role(
        name="user",
        display_name="Пользователь",
        description="Базовые права доступа",
        permissions=Permission.READ,
        is_system=True,
    ),

    "moderator": Role(
        name="moderator",
        display_name="Модератор",
        description="Права на модерацию контента",
        permissions=Permission.READ | Permission.WRITE | Permission.VIEW_STATS,
        is_system=True,
    ),

    "admin": Role(
        name="admin",
        display_name="Администратор",
        description="Полный доступ к системе",
        permissions=Permission.FULL_ACCESS,
        is_system=True,
    ),
}
