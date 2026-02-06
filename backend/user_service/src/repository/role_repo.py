"""
Работа с ролями
Реализация репозитория для CRUD операций с ролями
"""

from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any

from backend.user_service.src.models import RoleModel


class RoleRepository:
    """Репозиторий для работы с ролями пользователей"""

    def __init__(self, db_session: Session):
        self.db = db_session

    # === Синхронные методы ===

    def get_role_by_id(self, role_id: UUID) -> Optional[RoleModel]:
        """Получение роли по ID"""
        return self.db.query(RoleModel).filter(
            and_(
                RoleModel.id == role_id,
                RoleModel.is_active == True
            )
        ).first()

    def get_role_by_name(self, name: str) -> Optional[RoleModel]:
        """Получение роли по имени"""
        return self.db.query(RoleModel).filter(
            and_(
                RoleModel.name == name,
                RoleModel.is_active == True
            )
        ).first()

    def create_role(
        self,
        name: str,
        permissions: int,
        description: str = "",
        is_active: bool = True,
        display_name: str = "",
        is_system: bool = False
    ) -> RoleModel:
        """Создание новой роли"""
        if self.get_role_by_name(name):
            raise ValueError(f"Роль с именем '{name}' уже существует")

        role = RoleModel(
            name=name,
            display_name=display_name or name,
            permissions=permissions,
            description=description,
            is_active=is_active,
            is_system=is_system
        )

        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)

        return role

    def update_role(
        self,
        role_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[RoleModel]:
        """Обновление роли"""
        role = self.get_role_by_id(role_id)
        if not role:
            return None

        for field, value in updates.items():
            if hasattr(role, field):
                setattr(role, field, value)

        self.db.commit()
        self.db.refresh(role)

        return role

    def delete_role(self, role_id: UUID) -> bool:
        """Удаление роли (мягкое)"""
        role = self.get_role_by_id(role_id)
        if not role:
            return False

        role.is_active = False
        self.db.commit()
        return True

    def list_active_roles(self) -> List[RoleModel]:
        """Получение списка всех активных ролей"""
        return self.db.query(RoleModel).filter(
            RoleModel.is_active == True
        ).order_by(RoleModel.name).all()

    def get_user_count_for_role(self, role_id: UUID) -> int:
        """Получение количества пользователей с определенной ролью"""
        role = self.get_role_by_id(role_id)
        if not role:
            return 0
        return len(role.users)

    def get_roles_with_user_count(self) -> List[Dict[str, Any]]:
        """Получение ролей с количеством пользователей"""
        roles = self.list_active_roles()
        result = []

        for role in roles:
            result.append({
                'id': role.id,
                'name': role.name,
                'display_name': role.display_name,
                'description': role.description,
                'permissions': role.permissions,
                'is_active': role.is_active,
                'is_system': role.is_system,
                'user_count': len(role.users),
                'created_at': role.created_at,
                'updated_at': role.updated_at
            })

        return result

    def search_roles(self, search_term: str, limit: int = 50) -> List[RoleModel]:
        """Поиск ролей по названию или описанию"""
        return self.db.query(RoleModel).filter(
            and_(
                RoleModel.is_active == True,
                RoleModel.name.ilike(f"%{search_term}%")
            )
        ).limit(limit).all()

    def role_exists(self, name: str) -> bool:
        """Проверка существования роли по имени"""
        return self.get_role_by_name(name) is not None

    # === Асинхронные методы для совместимости с usecases ===

    async def get_by_id(self, role_id: str) -> Optional[RoleModel]:
        """Получение роли по ID (async wrapper)"""
        try:
            uuid_id = UUID(role_id)
        except ValueError:
            return None
        return self.get_role_by_id(uuid_id)

    async def get_by_name(self, name: str) -> Optional[RoleModel]:
        """Получение роли по имени (async wrapper)"""
        return self.get_role_by_name(name)

    async def create(self, role_data: Dict[str, Any]) -> RoleModel:
        """Создание роли (async wrapper)"""
        return self.create_role(
            name=role_data["name"],
            permissions=role_data["permissions"],
            description=role_data.get("description", ""),
            is_active=role_data.get("is_active", True),
            display_name=role_data.get("display_name", role_data["name"]),
            is_system=role_data.get("is_system", False)
        )

    async def update(self, role_id: str, updates: Dict[str, Any]) -> Optional[RoleModel]:
        """Обновление роли (async wrapper)"""
        try:
            uuid_id = UUID(role_id)
        except ValueError:
            return None
        return self.update_role(uuid_id, updates)

    async def delete(self, role_id: str) -> bool:
        """Удаление роли (async wrapper)"""
        try:
            uuid_id = UUID(role_id)
        except ValueError:
            return False
        return self.delete_role(uuid_id)

    async def get_all_active(self) -> List[RoleModel]:
        """Получение всех активных ролей (async wrapper)"""
        return self.list_active_roles()
