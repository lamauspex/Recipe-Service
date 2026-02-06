"""
Инфраструктурный сервис для управления пользователями
"""

import logging
from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime, timedelta

from ...interfaces.admin import UserManagementInterface
from ...dto.requests import (
    UserListRequestDTO,
    UserStatusUpdateRequestDTO,
    UserDeleteRequestDTO,
    UserActivityRequestDTO,
    UserSearchRequestDTO
)
from ...dto.responses import (
    UserListResponseDTO,
    UserDetailResponseDTO,
    UserStatusResponseDTO,
    UserDeleteResponseDTO,
    UserActivityResponseDTO,
    UserSearchResponseDTO
)
from ..common.exceptions import NotFoundException, ValidationException


logger = logging.getLogger(__name__)


class UserManagementService(UserManagementInterface):
    """Сервис для управления пользователями"""

    def __init__(
        self,
        user_repository,
        activity_repository=None,
        get_users_usecase=None,
        get_user_by_id_usecase=None,
        update_user_status_usecase=None,
        delete_user_usecase=None,
        get_user_activity_usecase=None,
        search_users_usecase=None,
        **kwargs
    ):
        self.user_repository = user_repository
        self.activity_repository = activity_repository
        
        # Usecases
        self.get_users_usecase = get_users_usecase
        self.get_user_by_id_usecase = get_user_by_id_usecase
        self.update_user_status_usecase = update_user_status_usecase
        self.delete_user_usecase = delete_user_usecase
        self.get_user_activity_usecase = get_user_activity_usecase
        self.search_users_usecase = search_users_usecase

    async def get_users(self, request: UserListRequestDTO) -> UserListResponseDTO:
        """Получение списка пользователей с фильтрацией"""
        try:
            logger.info(f"Getting users list: page={request.page}, per_page={request.per_page}")
            
            if self.get_users_usecase:
                return await self.get_users_usecase.execute(request)
            else:
                # Fallback реализация без usecase
                return await self._get_users_fallback(request)
                
        except Exception as e:
            logger.error(f"Error getting users list: {str(e)}")
            raise ValidationException(f"Failed to get users: {str(e)}")

    async def get_user_by_id(self, user_id: str) -> UserDetailResponseDTO:
        """Получение пользователя по ID"""
        try:
            logger.info(f"Getting user by ID: {user_id}")
            
            if self.get_user_by_id_usecase:
                return await self.get_user_by_id_usecase.execute(user_id)
            else:
                # Fallback реализация без usecase
                return await self._get_user_by_id_fallback(user_id)
                
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise ValidationException(f"Failed to get user: {str(e)}")

    async def update_user_status(self, request: UserStatusUpdateRequestDTO) -> UserStatusResponseDTO:
        """Обновление статуса пользователя"""
        try:
            logger.info(f"Updating user status: {request.user_id} -> {request.status}")
            
            if self.update_user_status_usecase:
                return await self.update_user_status_usecase.execute(request)
            else:
                # Fallback реализация без usecase
                return await self._update_user_status_fallback(request)
                
        except Exception as e:
            logger.error(f"Error updating user status for {request.user_id}: {str(e)}")
            raise ValidationException(f"Failed to update user status: {str(e)}")

    async def delete_user(self, request: UserDeleteRequestDTO) -> UserDeleteResponseDTO:
        """Удаление пользователя (мягкое удаление)"""
        try:
            logger.info(f"Deleting user: {request.user_id}")
            
            if self.delete_user_usecase:
                return await self.delete_user_usecase.execute(request)
            else:
                # Fallback реализация без usecase
                return await self._delete_user_fallback(request)
                
        except Exception as e:
            logger.error(f"Error deleting user {request.user_id}: {str(e)}")
            raise ValidationException(f"Failed to delete user: {str(e)}")

    async def get_user_activity(self, request: UserActivityRequestDTO) -> UserActivityResponseDTO:
        """Получение активности пользователя"""
        try:
            logger.info(f"Getting user activity: {request.user_id}, days={request.days}")
            
            if self.get_user_activity_usecase:
                return await self.get_user_activity_usecase.execute(request)
            else:
                # Fallback реализация без usecase
                return await self._get_user_activity_fallback(request)
                
        except Exception as e:
            logger.error(f"Error getting user activity for {request.user_id}: {str(e)}")
            raise ValidationException(f"Failed to get user activity: {str(e)}")

    async def search_users(self, request: UserSearchRequestDTO) -> UserSearchResponseDTO:
        """Поиск пользователей"""
        try:
            logger.info(f"Searching users: '{request.search_term}', limit={request.limit}")
            
            if self.search_users_usecase:
                return await self.search_users_usecase.execute(request)
            else:
                # Fallback реализация без usecase
                return await self._search_users_fallback(request)
                
        except Exception as e:
            logger.error(f"Error searching users with term '{request.search_term}': {str(e)}")
            raise ValidationException(f"Failed to search users: {str(e)}")

    # === Fallback методы (упрощенные реализации) ===

    async def _get_users_fallback(self, request: UserListRequestDTO) -> UserListResponseDTO:
        """Fallback реализация получения пользователей"""
        # Базовая реализация без usecase
        users_data = await self.user_repository.get_users_with_pagination(
            page=request.page,
            per_page=request.per_page,
            search=request.search,
            is_active=request.is_active,
            is_locked=request.is_locked
        )
        
        # Преобразование в простые DTO
        users = []
        for user_data in users_data.get('users', []):
            user_dto = {
                "id": user_data['id'],
                "email": user_data['email'],
                "first_name": user_data.get('first_name'),
                "last_name": user_data.get('last_name'),
                "phone": user_data.get('phone'),
                "role": user_data.get('role', 'user'),
                "is_active": user_data['is_active'],
                "is_verified": user_data.get('is_verified', False),
                "created_at": user_data['created_at'],
                "updated_at": user_data['updated_at']
            }
            users.append(user_dto)

        return UserListResponseDTO.create_success(
            users=users,
            total=users_data.get('total', 0),
            page=request.page,
            per_page=request.per_page
        )

    async def _get_user_by_id_fallback(self, user_id: str) -> UserDetailResponseDTO:
        """Fallback реализация получения пользователя по ID"""
        user_data = await self.user_repository.get_by_id(user_id)
        
        if not user_data:
            raise NotFoundException("User not found")

        user_detail_data = {
            "id": str(user_data['id']),
            "email": user_data['email'],
            "full_name": user_data.get('full_name') or f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}",
            "first_name": user_data.get('first_name'),
            "last_name": user_data.get('last_name'),
            "phone": user_data.get('phone'),
            "is_active": user_data['is_active'],
            "is_verified": user_data.get('is_verified', False),
            "created_at": user_data['created_at'].isoformat(),
            "updated_at": user_data['updated_at'].isoformat()
        }

        return UserDetailResponseDTO.create_success(user_detail_data)

    async def _update_user_status_fallback(self, request: UserStatusUpdateRequestDTO) -> UserStatusResponseDTO:
        """Fallback реализация обновления статуса"""
        update_data = {}
        
        if request.status == 'activate':
            update_data = {'is_active': True, 'is_locked': False}
        elif request.status == 'deactivate':
            update_data = {'is_active': False, 'is_locked': True}
        elif request.status == 'lock':
            update_data = {'is_locked': True}
        elif request.status == 'unlock':
            update_data = {'is_locked': False}

        updated_user = await self.user_repository.update(request.user_id, update_data)
        
        if not updated_user:
            raise ValidationException("Failed to update user status")

        return UserStatusResponseDTO.create_success(
            user_id=str(request.user_id),
            status=request.status
        )

    async def _delete_user_fallback(self, request: UserDeleteRequestDTO) -> UserDeleteResponseDTO:
        """Fallback реализация удаления пользователя"""
        update_data = {
            'is_active': False,
            'is_deleted': True,
            'deleted_at': datetime.utcnow()
        }

        updated_user = await self.user_repository.update(request.user_id, update_data)
        
        if not updated_user:
            raise ValidationException("Failed to delete user")

        return UserDeleteResponseDTO.create_success(
            user_id=int(request.user_id)
        )

    async def _get_user_activity_fallback(self, request: UserActivityRequestDTO) -> UserActivityResponseDTO:
        """Fallback реализация получения активности"""
        user_data = await self.user_repository.get_by_id(request.user_id)
        
        if not user_data:
            raise NotFoundException("User not found")

        activity_data = {
            "user_id": str(request.user_id),
            "period_days": request.days,
            "login_count": user_data.get('login_count', 0),
            "last_login_at": user_data.get('last_login_at'),
            "last_login_ip": user_data.get('last_login_ip')
        }

        return UserActivityResponseDTO.create_success(activity_data)

    async def _search_users_fallback(self, request: UserSearchRequestDTO) -> UserSearchResponseDTO:
        """Fallback реализация поиска пользователей"""
        users_data = await self.user_repository.search_users(
            search_term=request.search_term,
            limit=request.limit
        )

        results = []
        for user_data in users_data:
            result = {
                "id": str(user_data['id']),
                "email": user_data['email'],
                "full_name": user_data.get('full_name') or f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}",
                "is_active": user_data['is_active']
            }
            results.append(result)

        return UserSearchResponseDTO.create_success(
            search_term=request.search_term,
            results=results,
            total_found=len(results)
        )
