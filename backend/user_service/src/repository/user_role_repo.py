"""
Работа со связями пользователей и ролей
Реализация репозитория для управления связями многие-ко-многим
"""

from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, select

from backend.user_service.src.models import User, RoleModel, user_roles


class UserRoleRepository:
    """Репозиторий для работы со связями пользователей и ролей"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> bool:
        """Назначение роли пользователю"""
        # Проверка существования
        user = self.db.query(User).filter(User.id == user_id).first()
        role = self.db.query(RoleModel).filter(RoleModel.id == role_id).first()

        if not user:
            raise ValueError(f"Пользователь с ID {user_id} не найден")
        if not role:
            raise ValueError(f"Роль с ID {role_id} не найдена")
        if not role.is_active:
            raise ValueError(f"Роль '{role.name}' неактивна")

        # Проверка связи через SQL
        stmt = select(user_roles).where(
            and_(
                user_roles.c.user_id == user_id,
                user_roles.c.role_id == role_id
            )
        )
        existing = self.db.execute(stmt).first()

        if existing:
            raise ValueError(f"У пользователя уже есть роль '{role.name}'")

        # Создание связи
        self.db.execute(
            user_roles.insert().values(user_id=user_id, role_id=role_id)
        )
        self.db.commit()

        return True

    def remove_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        """Удаление роли у пользователя"""
        result = self.db.execute(
            user_roles.delete().where(
                and_(
                    user_roles.c.user_id == user_id,
                    user_roles.c.role_id == role_id
                )
            )
        )
        self.db.commit()
        return result.rowcount > 0

    def get_user_roles(self, user_id: UUID) -> List[RoleModel]:
        """Получение всех ролей пользователя"""
        stmt = (
            select(RoleModel)
            .join(user_roles, RoleModel.id == user_roles.c.role_id)
            .where(
                and_(
                    user_roles.c.user_id == user_id,
                    RoleModel.is_active == True
                )
            )
            .order_by(RoleModel.name)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def get_role_users(self, role_id: UUID) -> List[User]:
        """Получение всех пользователей с ролью"""
        stmt = (
            select(User)
            .join(user_roles, User.id == user_roles.c.user_id)
            .where(
                and_(
                    user_roles.c.role_id == role_id,
                    User.status == "active"
                )
            )
            .order_by(User.user_name)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def user_has_role(self, user_id: UUID, role_name: str) -> bool:
        """Проверка наличия роли у пользователя"""
        stmt = (
            select(RoleModel)
            .join(user_roles, RoleModel.id == user_roles.c.role_id)
            .where(
                and_(
                    user_roles.c.user_id == user_id,
                    RoleModel.name == role_name,
                    RoleModel.is_active == True
                )
            )
        )
        result = self.db.execute(stmt).first()
        return result is not None

    def get_user_role_count(self, user_id: UUID) -> int:
        """Количество ролей у пользователя"""
        stmt = select(user_roles).where(user_roles.c.user_id == user_id)
        return len(self.db.execute(stmt).fetchall())

    def get_role_assignment_count(self, role_id: UUID) -> int:
        """Количество пользователей с ролью"""
        stmt = select(user_roles).where(user_roles.c.role_id == role_id)
        return len(self.db.execute(stmt).fetchall())

    def remove_all_user_roles(self, user_id: UUID) -> bool:
        """Удаление всех ролей у пользователя"""
        self.db.execute(
            user_roles.delete().where(user_roles.c.user_id == user_id)
        )
        self.db.commit()
        return True
