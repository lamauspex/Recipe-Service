"""
UserRole Repository - репозиторий для управления связями пользователей и ролей
Создан на основе функциональности из старого user_role_repo.py
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, select, func

from ...interfaces.user_role import UserRoleRepositoryInterface
from ...infrastructure.common.exceptions import (
    NotFoundException,
    ValidationException,
    DatabaseException
)

# Импорт реальных моделей (заменить на ваши модели)
try:
    from backend.user_service.src.models import User, RoleModel, user_roles
except ImportError:
    # Временные заглушки для моделей
    class User:
        def __init__(self):
            self.id = "mock_user_id"
            self.email = "mock@example.com"
            self.status = "active"
            self.user_name = "mock_user"

    class RoleModel:
        def __init__(self):
            self.id = "mock_role_id"
            self.name = "mock_role"
            self.is_active = True

    class user_roles:
        """Заглушка для таблицы связей"""
        pass

    # Создаем mock для таблицы связей
    user_roles = type('user_roles', (), {'c': type('columns', (), {
        'user_id': 'user_id',
        'role_id': 'role_id'
    })()})()


class UserRoleRepository(UserRoleRepositoryInterface):
    """Репозиторий для работы со связями пользователей и ролей"""

    def __init__(self, db_session: Session, **kwargs):
        self.db = db_session

    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Назначение роли пользователю"""
        try:
            uuid_user_id = UUID(user_id)
            uuid_role_id = UUID(role_id)

            # Проверка существования пользователя
            user = self.db.query(User).filter(User.id == uuid_user_id).first()
            if not user:
                raise ValidationException(f"Пользователь с ID {user_id} не найден")

            # Проверка существования роли
            role = self.db.query(RoleModel).filter(
                and_(
                    RoleModel.id == uuid_role_id,
                    RoleModel.is_active == True
                )
            ).first()
            if not role:
                raise ValidationException(f"Роль с ID {role_id} не найдена или неактивна")

            # Проверка, не назначена ли уже эта роль
            existing_assignment = self.db.execute(
                select(user_roles).where(
                    and_(
                        user_roles.c.user_id == uuid_user_id,
                        user_roles.c.role_id == uuid_role_id
                    )
                )
            ).first()

            if existing_assignment:
                raise ValidationException(f"Пользователю уже назначена роль '{role.name}'")

            # Создание связи
            self.db.execute(
                user_roles.insert().values(
                    user_id=uuid_user_id,
                    role_id=uuid_role_id
                )
            )
            self.db.commit()
            return True

        except ValueError:
            raise ValidationException("Некорректный формат ID")
        except ValidationException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Ошибка при назначении роли пользователю: {str(e)}")

    async def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """Удаление роли у пользователя"""
        try:
            uuid_user_id = UUID(user_id)
            uuid_role_id = UUID(role_id)

            result = self.db.execute(
                user_roles.delete().where(
                    and_(
                        user_roles.c.user_id == uuid_user_id,
                        user_roles.c.role_id == uuid_role_id
                    )
                )
            )
            self.db.commit()
            return result.rowcount > 0

        except ValueError:
            return False
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Ошибка при удалении роли у пользователя: {str(e)}")

    async def get_user_roles(self, user_id: str) -> List[RoleModel]:
        """Получение всех ролей пользователя"""
        try:
            uuid_user_id = UUID(user_id)
            
            stmt = (
                select(RoleModel)
                .join(user_roles, RoleModel.id == user_roles.c.role_id)
                .where(
                    and_(
                        user_roles.c.user_id == uuid_user_id,
                        RoleModel.is_active == True
                    )
                )
                .order_by(RoleModel.name)
            )
            
            result = self.db.execute(stmt)
            return list(result.scalars().all())

        except ValueError:
            return []
        except Exception as e:
            raise DatabaseException(f"Ошибка при получении ролей пользователя: {str(e)}")

    async def get_role_users(self, role_id: str) -> List[User]:
        """Получение всех пользователей с ролью"""
        try:
            uuid_role_id = UUID(role_id)
            
            stmt = (
                select(User)
                .join(user_roles, User.id == user_roles.c.user_id)
                .join(RoleModel, user_roles.c.role_id == RoleModel.id)
                .where(
                    and_(
                        user_roles.c.role_id == uuid_role_id,
                        RoleModel.is_active == True,
                        User.status == "active"  # Предполагаем поле status в User
                    )
                )
                .order_by(User.user_name)
            )
            
            result = self.db.execute(stmt)
            return list(result.scalars().all())

        except ValueError:
            return []
        except Exception as e:
            raise DatabaseException(f"Ошибка при получении пользователей с ролью: {str(e)}")

    async def user_has_role(self, user_id: str, role_name: str) -> bool:
        """Проверка наличия роли у пользователя"""
        try:
            uuid_user_id = UUID(user_id)
            
            stmt = (
                select(RoleModel)
                .join(user_roles, RoleModel.id == user_roles.c.role_id)
                .where(
                    and_(
                        user_roles.c.user_id == uuid_user_id,
                        RoleModel.name == role_name.lower().strip(),
                        RoleModel.is_active == True
                    )
                )
            )
            
            result = self.db.execute(stmt).first()
            return result is not None

        except ValueError:
            return False
        except Exception as e:
            raise DatabaseException(f"Ошибка при проверке роли пользователя: {str(e)}")

    async def get_user_role_count(self, user_id: str) -> int:
        """Количество ролей у пользователя"""
        try:
            uuid_user_id = UUID(user_id)
            
            stmt = select(func.count(user_roles.c.role_id)).where(
                user_roles.c.user_id == uuid_user_id
            )
            
            result = self.db.execute(stmt).scalar()
            return result or 0

        except ValueError:
            return 0
        except Exception as e:
            raise DatabaseException(f"Ошибка при подсчете ролей пользователя: {str(e)}")

    async def get_role_assignment_count(self, role_id: str) -> int:
        """Количество пользователей с ролью"""
        try:
            uuid_role_id = UUID(role_id)
            
            stmt = select(func.count(user_roles.c.user_id)).where(
                user_roles.c.role_id == uuid_role_id
            )
            
            result = self.db.execute(stmt).scalar()
            return result or 0

        except ValueError:
            return 0
        except Exception as e:
            raise DatabaseException(f"Ошибка при подсчете пользователей с ролью: {str(e)}")

    async def remove_all_user_roles(self, user_id: str) -> bool:
        """Удаление всех ролей у пользователя"""
        try:
            uuid_user_id = UUID(user_id)
            
            self.db.execute(
                user_roles.delete().where(user_roles.c.user_id == uuid_user_id)
            )
            self.db.commit()
            return True

        except ValueError:
            return False
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Ошибка при удалении всех ролей пользователя: {str(e)}")

    # === Расширенная функциональность ===

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Получение разрешений пользователя через роли"""
        try:
            uuid_user_id = UUID(user_id)
            
            stmt = (
                select(RoleModel.permissions, RoleModel.permissions_list)
                .join(user_roles, RoleModel.id == user_roles.c.role_id)
                .where(
                    and_(
                        user_roles.c.user_id == uuid_user_id,
                        RoleModel.is_active == True
                    )
                )
            )
            
            result = self.db.execute(stmt).all()
            permissions = []
            
            for permissions_int, permissions_list in result:
                if permissions_list:
                    permissions.extend(permissions_list)
                elif permissions_int:
                    # Если permissions_list пустой, но есть permissions_int
                    # Здесь можно добавить логику конвертации битовых флагов в разрешения
                    pass
            
            return list(set(permissions))  # Убираем дубликаты

        except ValueError:
            return []
        except Exception as e:
            raise DatabaseException(f"Ошибка при получении разрешений пользователя: {str(e)}")

    async def check_user_permission(self, user_id: str, permission: str) -> bool:
        """Проверка разрешения пользователя"""
        try:
            permissions = await self.get_user_permissions(user_id)
            return permission in permissions

        except Exception as e:
            raise DatabaseException(f"Ошибка при проверке разрешения пользователя: {str(e)}")

    async def assign_multiple_roles_to_user(self, user_id: str, role_ids: List[str]) -> Dict[str, Any]:
        """Назначение нескольких ролей пользователю"""
        try:
            uuid_user_id = UUID(user_id)
            assigned_roles = []
            errors = []

            for role_id in role_ids:
                try:
                    if await self.assign_role_to_user(user_id, role_id):
                        assigned_roles.append(role_id)
                    else:
                        errors.append(f"Роль {role_id} уже назначена или не найдена")
                except ValidationException as e:
                    errors.append(str(e))
                except Exception as e:
                    errors.append(f"Ошибка назначения роли {role_id}: {str(e)}")

            return {
                "success": True,
                "user_id": user_id,
                "assigned_roles": assigned_roles,
                "errors": errors,
                "total_attempted": len(role_ids)
            }

        except Exception as e:
            raise DatabaseException(f"Ошибка при назначении нескольких ролей: {str(e)}")

    async def remove_multiple_roles_from_user(self, user_id: str, role_ids: List[str]) -> Dict[str, Any]:
        """Удаление нескольких ролей у пользователя"""
        try:
            removed_roles = []
            errors = []

            for role_id in role_ids:
                try:
                    if await self.remove_role_from_user(user_id, role_id):
                        removed_roles.append(role_id)
                    else:
                        errors.append(f"Роль {role_id} не найдена у пользователя")
                except Exception as e:
                    errors.append(f"Ошибка удаления роли {role_id}: {str(e)}")

            return {
                "success": True,
                "user_id": user_id,
                "removed_roles": removed_roles,
                "errors": errors,
                "total_attempted": len(role_ids)
            }

        except Exception as e:
            raise DatabaseException(f"Ошибка при удалении нескольких ролей: {str(e)}")

    async def get_users_with_role(self, role_id: str) -> List[Dict[str, Any]]:
        """Получение пользователей с ролью и дополнительной информацией"""
        try:
            uuid_role_id = UUID(role_id)
            
            stmt = (
                select(
                    User.id,
                    User.email,
                    User.user_name,
                    user_roles.c.assigned_at
                )
                .join(user_roles, User.id == user_roles.c.user_id)
                .join(RoleModel, user_roles.c.role_id == RoleModel.id)
                .where(
                    and_(
                        user_roles.c.role_id == uuid_role_id,
                        RoleModel.is_active == True,
                        User.status == "active"
                    )
                )
                .order_by(User.user_name)
            )
            
            result = self.db.execute(stmt)
            users = []
            
            for user_id, email, user_name, assigned_at in result:
                users.append({
                    "user_id": str(user_id),
                    "email": email,
                    "username": user_name,
                    "assigned_at": assigned_at.isoformat() if assigned_at else None
                })
            
            return users

        except ValueError:
            return []
        except Exception as e:
            raise DatabaseException(f"Ошибка при получении пользователей с ролью: {str(e)}")

    async def get_roles_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Получение ролей пользователя с дополнительной информацией"""
        try:
            uuid_user_id = UUID(user_id)
            
            stmt = (
                select(
                    RoleModel.id,
                    RoleModel.name,
                    RoleModel.display_name,
                    RoleModel.description,
                    RoleModel.permissions,
                    user_roles.c.assigned_at
                )
                .join(user_roles, RoleModel.id == user_roles.c.role_id)
                .where(
                    and_(
                        user_roles.c.user_id == uuid_user_id,
                        RoleModel.is_active == True
                    )
                )
                .order_by(RoleModel.name)
            )
            
            result = self.db.execute(stmt)
            roles = []
            
            for role_id, name, display_name, description, permissions, assigned_at in result:
                roles.append({
                    "role_id": str(role_id),
                    "name": name,
                    "display_name": display_name,
                    "description": description,
                    "permissions": permissions,
                    "assigned_at": assigned_at.isoformat() if assigned_at else None
                })
            
            return roles

        except ValueError:
            return []
        except Exception as e:
            raise DatabaseException(f"Ошибка при получении ролей пользователя: {str(e)}")

    async def get_role_statistics(self) -> Dict[str, Any]:
        """Получение статистики по ролям и назначениям"""
        try:
            # Общая статистика
            total_assignments = self.db.query(func.count(user_roles.c.user_id)).scalar() or 0
            
            # Статистика по ролям
            role_stats = self.db.execute(
                select(
                    RoleModel.id,
                    RoleModel.name,
                    RoleModel.display_name,
                    func.count(user_roles.c.user_id).label('user_count')
                )
                .join(user_roles, RoleModel.id == user_roles.c.role_id, isouter=True)
                .where(RoleModel.is_active == True)
                .group_by(RoleModel.id, RoleModel.name, RoleModel.display_name)
            ).all()

            roles_info = []
            for role_id, name, display_name, user_count in role_stats:
                roles_info.append({
                    "role_id": str(role_id),
                    "name": name,
                    "display_name": display_name,
                    "user_count": user_count
                })

            # Пользователи с наибольшим количеством ролей
            top_users = self.db.execute(
                select(
                    User.id,
                    User.email,
                    User.user_name,
                    func.count(user_roles.c.role_id).label('role_count')
                )
                .join(user_roles, User.id == user_roles.c.user_id, isouter=True)
                .join(RoleModel, user_roles.c.role_id == RoleModel.id, isouter=True)
                .where(
                    and_(
                        RoleModel.is_active == True,
                        User.status == "active"
                    )
                )
                .group_by(User.id, User.email, User.user_name)
                .order_by(desc('role_count'))
                .limit(10)
            ).all()

            top_users_info = []
            for user_id, email, user_name, role_count in top_users:
                top_users_info.append({
                    "user_id": str(user_id),
                    "email": email,
                    "username": user_name,
                    "role_count": role_count
                })

            return {
                "total_assignments": total_assignments,
                "roles_info": roles_info,
                "top_users": top_users_info,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            raise DatabaseException(f"Ошибка при получении статистики ролей: {str(e)}")

    async def cleanup_orphaned_assignments(self) -> Dict[str, Any]:
        """Очистка осиротевших назначений ролей"""
        try:
            # Удаляем назначения для несуществующих пользователей
            orphaned_user_assignments = self.db.execute(
                user_roles.delete().where(
                    ~user_roles.c.user_id.in_(
                        select(User.id)
                    )
                )
            ).rowcount

            # Удаляем назначения для несуществующих ролей
            orphaned_role_assignments = self.db.execute(
                user_roles.delete().where(
                    ~user_roles.c.role_id.in_(
                        select(RoleModel.id).where(RoleModel.is_active == True)
                    )
                )
            ).rowcount

            self.db.commit()

            return {
                "success": True,
                "orphaned_user_assignments_removed": orphaned_user_assignments,
                "orphaned_role_assignments_removed": orphaned_role_assignments,
                "total_removed": orphaned_user_assignments + orphaned_role_assignments,
                "performed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Ошибка при очистке осиротевших назначений: {str(e)}")
