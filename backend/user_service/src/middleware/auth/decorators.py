"""Декораторы для авторизации"""

from fastapi import HTTPException, status
from typing import Callable, List
from functools import wraps

from user_service.models import User
from user_service.schemas import Permission


# ========= Базовые декораторы =========
def require_admin(func: Callable) -> Callable:
    """Декоратор для require_admin доступа к эндпоинтам"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = _extract_user_from_args(args, kwargs)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Требуется аутентификация"
            )
        if not current_user.has_permission(Permission.MANAGE_USERS):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции"
            )
        return await func(*args, **kwargs)
    return wrapper


def require_active_user(func: Callable) -> Callable:
    """Декоратор для require_active_user доступа к эндпоинтам"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = _extract_user_from_args(args, kwargs)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Требуется аутентификация"
            )
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь неактивен"
            )
        return await func(*args, **kwargs)
    return wrapper


def require_role(role_name: str):
    """Декоратор для require_role доступа к эндпоинтам"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = _extract_user_from_args(args, kwargs)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется аутентификация"
                )
            has_role = current_user.has_role(role_name.lower())
            if not has_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Требуется роль: {role_name}"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ========= Продвинутые декораторы для разрешений =========
def require_permission(permission: str):
    """Декоратор для require_permission доступа к эндпоинтам"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = _extract_user_from_args(args, kwargs)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется аутентификация"
                )
            try:
                perm = Permission[permission.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Неизвестное разрешение: {permission}"
                )
            if not current_user.has_permission(perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"Недостаточно прав. "
                        f"Требуется разрешение: {permission}"
                    )
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_permissions(permissions: List[str]):
    """Декоратор для require_permissions (все разрешения)"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = _extract_user_from_args(args, kwargs)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется аутентификация"
                )
            missing = []
            for perm_name in permissions:
                try:
                    perm = Permission[perm_name.upper()]
                except KeyError:
                    continue
                if not current_user.has_permission(perm):
                    missing.append(perm_name)
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": "Недостаточно прав",
                        "missing_permissions": missing,
                        "required_permissions": permissions
                    }
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(permissions: List[str]):
    """Декоратор для require_any_permission (хотя бы одно разрешение)"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = _extract_user_from_args(args, kwargs)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Требуется аутентификация"
                )
            has_any = False
            for perm_name in permissions:
                try:
                    perm = Permission[perm_name.upper()]
                except KeyError:
                    continue
                if current_user.has_permission(perm):
                    has_any = True
                    break
            if not has_any:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": "Недостаточно прав",
                        "required_permissions": permissions,
                        "detail": "Требуется хотя бы одно из разрешений"
                    }
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# ========= Вспомогательные функции =========


def _extract_user_from_args(args, kwargs) -> User:
    """Извлечение пользователя из аргументов функции"""

    for arg in args:
        if isinstance(arg, User):
            return arg
    return kwargs.get('current_user')
