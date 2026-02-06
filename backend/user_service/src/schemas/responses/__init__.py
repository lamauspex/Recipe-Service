"""
Базовые DTO для ответов
"""


from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class BaseResponseDTO(BaseModel):
    """Базовый DTO для ответов"""
    success: bool = True
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponseDTO(BaseResponseDTO):
    """DTO для ответов с ошибками"""
    success: bool = False
    error_code: str
    details: Optional[Dict[str, Any]] = None


class UserResponseDTO(BaseModel):
    """DTO для данных пользователя"""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, user) -> 'UserResponseDTO':
        """Создание DTO из ORM модели"""
        return cls(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=getattr(user, 'phone', None),
            role=getattr(user, 'role', 'user'),
            is_active=user.is_active,
            is_verified=getattr(user, 'is_verified', False),
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    @classmethod
    def create_success(cls, user: 'UserResponseDTO', message: str = None) -> 'UserResponseDTO':
        """Создание успешного ответа с пользователем"""
        return cls(
            success=True,
            message=message or "User retrieved successfully",
            data={"user": user.dict()}
        )


class AuthTokensDTO(BaseModel):
    """DTO для токенов авторизации"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class LoginResponseDTO(BaseResponseDTO):
    """DTO для ответа авторизации"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(
        cls,
        user: UserResponseDTO,
        tokens: AuthTokensDTO
    ) -> "LoginResponseDTO":
        return cls(
            data={
                "user": user.dict(),
                "tokens": tokens.dict()
            }
        )


class RegisterResponseDTO(BaseResponseDTO):
    """DTO для ответа регистрации"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user: UserResponseDTO) -> "RegisterResponseDTO":
        return cls(
            data={"user": user.dict()}
        )


class TokenRefreshResponseDTO(BaseResponseDTO):
    """DTO для ответа обновления токена"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(
        cls,
        tokens: AuthTokensDTO
    ) -> "TokenRefreshResponseDTO":
        return cls(
            data={"tokens": tokens.dict()}
        )


class UserListResponseDTO(BaseResponseDTO):
    """DTO для списка пользователей"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(
        cls,
        users: List[UserResponseDTO],
        total: int,
        page: int,
        per_page: int
    ) -> "UserListResponseDTO":
        return cls(
            data={
                "users": [user.dict() for user in users],
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "pages": (total + per_page - 1) // per_page
                }
            }
        )


class UserCreateResponseDTO(BaseResponseDTO):
    """DTO для ответа создания пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user: UserResponseDTO) -> "UserCreateResponseDTO":
        return cls(
            data={"user": user.dict()}
        )


class UserUpdateResponseDTO(BaseResponseDTO):
    """DTO для ответа обновления пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user: UserResponseDTO) -> "UserUpdateResponseDTO":
        return cls(
            data={"user": user.dict()}
        )


class UserDeleteResponseDTO(BaseResponseDTO):
    """DTO для ответа удаления пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_id: int) -> "UserDeleteResponseDTO":
        return cls(
            data={"deleted_user_id": user_id}
        )


class PasswordResetResponseDTO(BaseResponseDTO):
    """DTO для ответа сброса пароля"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, message: str) -> "PasswordResetResponseDTO":
        return cls(
            message=message
        )


class LogoutResponseDTO(BaseResponseDTO):
    """DTO для ответа выхода"""
    @classmethod
    def create_success(cls) -> "LogoutResponseDTO":
        return cls(message="Successfully logged out")


# === DTO для управления пользователями ===

class UserDetailResponseDTO(BaseResponseDTO):
    """DTO для детальной информации о пользователе"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_data: Dict[str, Any]) -> "UserDetailResponseDTO":
        return cls(
            data={"user": user_data}
        )


class UserStatusResponseDTO(BaseResponseDTO):
    """DTO для ответа обновления статуса пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_id: str, status: str) -> "UserStatusResponseDTO":
        return cls(
            data={
                "user_id": user_id,
                "status": status
            },
            message=f"User status updated to {status}"
        )


class UserActivityResponseDTO(BaseResponseDTO):
    """DTO для активности пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, activity_data: Dict[str, Any]) -> "UserActivityResponseDTO":
        return cls(
            data=activity_data
        )


class UserSearchResponseDTO(BaseResponseDTO):
    """DTO для результатов поиска пользователей"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(
        cls,
        search_term: str,
        results: List[Dict[str, Any]],
        total_found: int
    ) -> "UserSearchResponseDTO":
        return cls(
            data={
                "search_term": search_term,
                "results": results,
                "total_found": total_found
            }
        )

# === DTO для управления ролями ===


class UserRoleResponseDTO(BaseResponseDTO):
    """DTO для ответа на запрос на получение ролей пользователей"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_id: str, roles: List[Dict[str, Any]]) -> "UserRoleResponseDTO":
        return cls(
            data={
                "user_id": user_id,
                "roles": roles
            }
        )


class RoleResponseDTO(BaseModel):
    """DTO для данных роли"""
    id: str
    name: str
    display_name: str
    description: Optional[str] = None
    permissions: int
    permissions_list: List[str]
    is_system: bool
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class RoleCreateResponseDTO(BaseResponseDTO):
    """DTO для ответа создания роли"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, role: RoleResponseDTO) -> "RoleCreateResponseDTO":
        return cls(
            data={"role": role.dict()}
        )


class RoleUpdateResponseDTO(BaseResponseDTO):
    """DTO для ответа обновления роли"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, role: RoleResponseDTO) -> "RoleUpdateResponseDTO":
        return cls(
            data={"role": role.dict()}
        )


class RoleDeleteResponseDTO(BaseResponseDTO):
    """DTO для ответа удаления роли"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, role_id: str) -> "RoleDeleteResponseDTO":
        return cls(
            data={"deleted_role_id": role_id}
        )


class RoleListResponseDTO(BaseResponseDTO):
    """DTO для списка ролей"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(
        cls,
        roles: List[RoleResponseDTO],
        total: int
    ) -> "RoleListResponseDTO":
        return cls(
            data={
                "roles": [role.dict() for role in roles],
                "total": total
            }
        )


class RoleAssignResponseDTO(BaseResponseDTO):
    """DTO для ответа назначения роли"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_id: str, role_id: str) -> "RoleAssignResponseDTO":
        return cls(
            data={
                "user_id": user_id,
                "role_id": role_id
            },
            message="Role assigned successfully"
        )


class PermissionCheckResponseDTO(BaseResponseDTO):
    """DTO для ответа проверки разрешений"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_id: str, permission: str, has_permission: bool) -> "PermissionCheckResponseDTO":
        return cls(
            data={
                "user_id": user_id,
                "permission": permission,
                "has_permission": has_permission
            }
        )


class UserPermissionsResponseDTO(BaseResponseDTO):
    """DTO для ответа управления разрешениями пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_id: str, permissions: List[str]) -> "UserPermissionsResponseDTO":
        return cls(
            data={
                "user_id": user_id,
                "permissions": permissions
            }
        )


class UserLockResponseDTO(BaseResponseDTO):
    """DTO для ответа блокировки пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_id: str, reason: Optional[str] = None, duration_hours: Optional[int] = None) -> "UserLockResponseDTO":
        return cls(
            data={
                "user_id": user_id,
                "reason": reason,
                "duration_hours": duration_hours
            },
            message="User locked successfully"
        )


class UserUnlockResponseDTO(BaseResponseDTO):
    """DTO для ответа разблокировки пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_id: str) -> "UserUnlockResponseDTO":
        return cls(
            data={
                "user_id": user_id
            },
            message="User unlocked successfully"
        )


class UserLockStatusResponseDTO(BaseResponseDTO):
    """DTO для ответа статуса блокировки пользователя"""
    data: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_success(cls, user_id: str, is_locked: bool, lock_reason: Optional[str] = None, locked_until: Optional[str] = None) -> "UserLockStatusResponseDTO":
        return cls(
            data={
                "user_id": user_id,
                "is_locked": is_locked,
                "lock_reason": lock_reason,
                "locked_until": locked_until
            }
        )
