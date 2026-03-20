"""
simplify_roles_system

Revision ID: b12345678901
Revises: a7c53b6c4d00
Create Date: 2026-02-23 20:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b12345678901'
down_revision: Union[str, Sequence[str], None] = 'a7c53b6c4d00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Упрощение системы ролей: удаляем таблицы rolemodel и user_roles"""

    # 1. Удаляем связывающую таблицу user_roles
    op.drop_table('user_roles')

    # 2. Удаляем таблицу rolemodel
    op.drop_table('rolemodel')

    # 3. Добавляем колонку role_name в users (если ещё нет)
    # Проверяем и добавляем с значением по умолчанию 'user'
    op.add_column(
        'users',
        sa.Column(
            'role_name',
            sa.String(50),
            server_default='user',
            nullable=False,
            comment='Роль пользователя (user, moderator, admin)'
        )
    )

    # 4. Создаём индекс для role_name
    op.create_index(
        'ix_users_role_name',
        'users',
        ['role_name'],
        unique=False
    )


def downgrade() -> None:
    """Откат: восстанавливаем старую систему ролей"""

    # Удаляем индекс
    op.drop_index('ix_users_role_name', table_name='users')

    # Удаляем колонку role_name
    op.drop_column('users', 'role_name')

    # Восстанавливаем таблицу rolemodel
    op.create_table('rolemodel',
                    sa.Column('name', sa.String(50), nullable=False),
                    sa.Column('display_name', sa.String(100), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('permissions', sa.Integer(), nullable=False),
                    sa.Column('is_system', sa.Boolean(), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False),
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.create_index(op.f('ix_rolemodel_id'), 'rolemodel', ['id'])

    # Восстанавливаем таблицу user_roles
    op.create_table('user_roles',
                    sa.Column('user_id', sa.UUID(), nullable=False),
                    sa.Column('role_id', sa.UUID(), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['role_id'], ['rolemodel.id'], ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(
                        ['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('user_id', 'role_id')
                    )
