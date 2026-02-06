"""
Репозиторий для работы с ролями
Мигрирован из старого репозитория с async поддержкой и Clean Architecture
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm.query import Query

from ...interfaces.role import RoleRepositoryInterface
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)

# Импорт реальных моделей (заменить на ваши модели)
try:
    from backend.user_service.src.models import RoleModel
except ImportError:
    # Временная заглушка для модели Role
    class RoleModel:
        def __init__(self):
            self.id = "mock_role_id"
            self.name = "mock_role"
            self.display_name = "Mock Role"
            self.description = "Mock role description"
            self.permissions = 0
            self.permissions_list = []
            self.is_system = False
            self.is_active = True
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()


class RoleRepository(RoleRepositoryInterface):
    """Репозиторий для работы с ролями"""

    def __init__(self, db_session: Session, **kwargs):
        self.db = db_session

    async def get_by_id(self, role_id: str) -> Optional[RoleModel]:
        """Получение роли по ID"""
        try:
            uuid_id = UUID(role_id)
            role = self.db.query(RoleModel).filter(
                and_(
                    RoleModel.id == uuid_id,
                    RoleModel.is_active == True
                )
            ).first()
            return role
        except ValueError:
            return None

    async def get_by_name(self, name: str) -> Optional[RoleModel]:
        """Получение роли по имени"""
        return self.db.query(RoleModel).filter(
            and_(
                RoleModel.name == name.lower().strip(),
                RoleModel.is_active == True
            )
        ).first()

    async def create(self, role_data: Dict[str, Any]) -> RoleModel:
        """Создание роли"""
        try:
            name = role_data.get("name", "").lower().strip()

            # Проверяем уникальность имени
            if await self.role_exists(name):
                raise ValidationException(
                    f"Роль с именем '{name}' уже существует")

            role = RoleModel(
                name=name,
                display_name=role_data.get("display_name", name),
                permissions=role_data.get("permissions", 0),
                description=role_data.get("description", ""),
                is_active=role_data.get("is_active", True),
                is_system=role_data.get("is_system", False)
            )

            self.db.add(role)
            self.db.commit()
            self.db.refresh(role)
            return role
        except Exception as e:
            self.db.rollback()
            if "уже существует" in str(e):
                raise e
            raise DatabaseException(f"Ошибка при создании роли: {str(e)}")

    async def update(self, role_id: str, updates: Dict[str, Any]) -> Optional[RoleModel]:
        """Обновление роли"""
        try:
            uuid_id = UUID(role_id)
            role = self.db.query(RoleModel).filter(
                and_(
                    RoleModel.id == uuid_id,
                    RoleModel.is_active is True
                )
            ).first()

            if not role:
                return None

            # Обновляем поля роли
            for field, value in updates.items():
                if hasattr(role, field):
                    # Специальная обработка для name
                    if field == 'name' and value:
                        value = value.lower().strip()
                    setattr(role, field, value)

            role.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(role)
            return role
        except ValueError:
            return None
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Ошибка при обновлении роли: {str(e)}")

    async def delete(self, role_id: str) -> bool:
        """Мягкое удаление роли"""
        try:
            uuid_id = UUID(role_id)
            role = self.db.query(RoleModel).filter(
                and_(
                    RoleModel.id == uuid_id,
                    RoleModel.is_active is True
                )
            ).first()

            if not role:
                return False

            # Мягкое удаление - деактивация
            role.is_active = False
            role.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        except ValueError:
            return False
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Ошибка при удалении роли: {str(e)}")

    async def get_all_active(self) -> List[RoleModel]:
        """Получение всех активных ролей"""
        return self.db.query(RoleModel).filter(
            RoleModel.is_active is True
        ).order_by(RoleModel.name).all()

    async def list_active_roles(self) -> List[RoleModel]:
        """Получение списка всех активных ролей"""
        return await self.get_all_active()

    async def get_roles_with_user_count(self) -> List[Dict[str, Any]]:
        """Получение ролей с количеством пользователей"""
        try:
            roles = self.db.query(RoleModel).filter(
                RoleModel.is_active == True
            ).order_by(RoleModel.name).all()

            result = []
            for role in roles:
                # Подсчет пользователей с этой ролью (через связь many-to-many)
                user_count = await self.get_user_count_for_role(str(role.id))

                result.append({
                    'id': str(role.id),
                    'name': role.name,
                    'display_name': role.display_name,
                    'description': role.description,
                    'permissions': role.permissions,
                    'is_active': role.is_active,
                    'is_system': role.is_system,
                    'user_count': user_count,
                    'created_at': role.created_at.isoformat(),
                    'updated_at': role.updated_at.isoformat()
                })

            return result
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении ролей с количеством пользователей: {str(e)}")

    async def search_roles(self, search_term: str, limit: int = 50) -> List[RoleModel]:
        """Поиск ролей по названию или описанию"""
        search_term = search_term.lower().strip()
        return self.db.query(RoleModel).filter(
            and_(
                RoleModel.is_active == True,
                or_(
                    RoleModel.name.ilike(f"%{search_term}%"),
                    RoleModel.display_name.ilike(f"%{search_term}%"),
                    RoleModel.description.ilike(f"%{search_term}%")
                )
            )
        ).limit(limit).all()

    async def role_exists(self, name: str) -> bool:
        """Проверка существования роли по имени"""
        name = name.lower().strip()
        role = self.db.query(RoleModel).filter(
            and_(
                RoleModel.name == name,
                RoleModel.is_active == True
            )
        ).first()
        return role is not None

    async def get_user_count_for_role(self, role_id: str) -> int:
        """Получение количества пользователей с определенной ролью"""
        try:
            uuid_id = UUID(role_id)
            role = self.db.query(RoleModel).filter(
                and_(
                    RoleModel.id == uuid_id,
                    RoleModel.is_active == True
                )
            ).first()

            if not role:
                return 0

            # Подсчет пользователей через связь many-to-many
            # В реальном приложении это будет через association table
            user_count = len(getattr(role, 'users', []))
            return user_count
        except ValueError:
            return 0

    async def create_role(
        self,
        name: str,
        permissions: int,
        description: str = "",
        is_active: bool = True,
        display_name: str = "",
        is_system: bool = False
    ) -> RoleModel:
        """Создание новой роли (legacy метод для совместимости)"""
        role_data = {
            "name": name,
            "permissions": permissions,
            "description": description,
            "is_active": is_active,
            "display_name": display_name or name,
            "is_system": is_system
        }
        return await self.create(role_data)

    async def update_role(
        self,
        role_id: str,
        updates: Dict[str, Any]
    ) -> Optional[RoleModel]:
        """Обновление роли (legacy метод для совместимости)"""
        return await self.update(role_id, updates)

    async def delete_role(self, role_id: str) -> bool:
        """Удаление роли (legacy метод для совместимости)"""
        return await self.delete(role_id)

    async def list_active_roles_ordered(self) -> List[RoleModel]:
        """Получение списка всех активных ролей, отсортированных по имени"""
        return self.db.query(RoleModel).filter(
            RoleModel.is_active == True
        ).order_by(RoleModel.name).all()

    # === Дополнительные методы для расширенной функциональности ===

    async def get_system_roles(self) -> List[RoleModel]:
        """Получение системных ролей"""
        return self.db.query(RoleModel).filter(
            and_(
                RoleModel.is_active == True,
                RoleModel.is_system == True
            )
        ).order_by(RoleModel.name).all()

    async def get_custom_roles(self) -> List[RoleModel]:
        """Получение пользовательских ролей"""
        return self.db.query(RoleModel).filter(
            and_(
                RoleModel.is_active == True,
                RoleModel.is_system == False
            )
        ).order_by(RoleModel.name).all()

    async def get_roles_by_permission_level(self, min_permissions: int) -> List[RoleModel]:
        """Получение ролей с определенным уровнем разрешений"""
        return self.db.query(RoleModel).filter(
            and_(
                RoleModel.is_active == True,
                RoleModel.permissions >= min_permissions
            )
        ).order_by(desc(RoleModel.permissions)).all()

    async def duplicate_role(self, source_role_id: str, new_name: str, new_display_name: str = None) -> Optional[RoleModel]:
        """Создание копии роли"""
        try:
            source_role = await self.get_by_id(source_role_id)
            if not source_role:
                raise NotFoundException(
                    f"Исходная роль с ID {source_role_id} не найдена")

            # Проверяем уникальность нового имени
            if await self.role_exists(new_name):
                raise ValidationException(
                    f"Роль с именем '{new_name}' уже существует")

            role_data = {
                "name": new_name.lower().strip(),
                "display_name": new_display_name or new_name,
                "permissions": source_role.permissions,
                "description": f"Копия роли '{source_role.display_name}'",
                "is_active": True,
                "is_system": False  # Копия всегда пользовательская
            }

            return await self.create(role_data)
        except (NotFoundException, ValidationException):
            raise
        except Exception as e:
            raise DatabaseException(f"Ошибка при копировании роли: {str(e)}")

    async def get_roles_statistics(self) -> Dict[str, Any]:
        """Получение статистики по ролям"""
        try:
            total_roles = self.db.query(RoleModel).count()
            active_roles = self.db.query(RoleModel).filter(
                RoleModel.is_active == True).count()
            system_roles = self.db.query(RoleModel).filter(
                and_(
                    RoleModel.is_active == True,
                    RoleModel.is_system == True
                )
            ).count()
            custom_roles = self.db.query(RoleModel).filter(
                and_(
                    RoleModel.is_active == True,
                    RoleModel.is_system == False
                )
            ).count()

            # Статистика по разрешениям
            roles_with_permissions = self.db.query(RoleModel).filter(
                and_(
                    RoleModel.is_active == True,
                    RoleModel.permissions > 0
                )
            ).count()

            return {
                "total_roles": total_roles,
                "active_roles": active_roles,
                "inactive_roles": total_roles - active_roles,
                "system_roles": system_roles,
                "custom_roles": custom_roles,
                "roles_with_permissions": roles_with_permissions,
                "average_permissions": self.db.query(RoleModel.permissions).filter(
                    RoleModel.is_active == True
                ).avg() or 0
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при получении статистики ролей: {str(e)}")

    async def bulk_update_roles(self, updates: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Массовое обновление ролей"""
        try:
            updated_count = 0
            errors = []

            for role_id, role_updates in updates.items():
                try:
                    result = await self.update(role_id, role_updates)
                    if result:
                        updated_count += 1
                    else:
                        errors.append(f"Роль {role_id} не найдена")
                except Exception as e:
                    errors.append(
                        f"Ошибка обновления роли {role_id}: {str(e)}")

            return {
                "success": True,
                "updated_count": updated_count,
                "errors": errors,
                "total_attempted": len(updates)
            }
        except Exception as e:
            raise DatabaseException(
                f"Ошибка при массовом обновлении ролей: {str(e)}")
