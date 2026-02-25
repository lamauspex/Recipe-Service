"""
initial_migration

Revision ID: a7c53b6c4d00
Revises:
Create Date: 2025-12-30 00:18:00.671430

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7c53b6c4d00'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # СОЗДАЕМ ТАБЛИЦУ ROLEMODEL #############
    op.create_table('rolemodel',
                    sa.Column(
                        'name',
                        sa.String(50),
                        nullable=False,
                        comment='Системное имя роли (admin, user, moderator)'
                    ),
                    sa.Column(
                        'display_name',
                        sa.String(100),
                        nullable=False,
                        comment='Отображаемое имя (Администратор, Пользователь...)'
                    ),
                    sa.Column(
                        'description',
                        sa.Text(),
                        nullable=True,
                        comment='Описание роли'
                    ),
                    sa.Column(
                        'permissions',
                        sa.Integer(),
                        nullable=False,
                        comment='Битовая маска разрешений'
                    ),
                    sa.Column(
                        'is_system',
                        sa.Boolean(),
                        nullable=False,
                        comment='Системная роль (нельзя удалить)'
                    ),
                    sa.Column(
                        'is_active',
                        sa.Boolean(),
                        nullable=False,
                        comment='Активна ли роль'
                    ),
                    sa.Column(
                        'id',
                        sa.UUID(),
                        nullable=False,
                        comment='Уникальный идентификатор'
                    ),
                    sa.Column(
                        'created_at',
                        sa.DateTime(timezone=True),
                        server_default=sa.text('now()'),
                        nullable=False,
                        comment='Время создания записи'
                    ),
                    sa.Column(
                        'updated_at',
                        sa.DateTime(timezone=True),
                        server_default=sa.text('now()'),
                        nullable=True,
                        comment='Время последнего обновления'
                    ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )
    op.create_index(
        op.f('ix_rolemodel_id'),
        'rolemodel', ['id'],
        unique=False
    )

    # СОЗДАЕМ ТАБЛИЦУ USERS #############
    op.create_table('users',
                    sa.Column(
                        'user_name',
                        sa.String(50),
                        nullable=False,
                        comment='Имя пользователя'
                    ),
                    sa.Column(
                        'email',
                        sa.String(100),
                        nullable=False,
                        comment='Email пользователя'
                    ),
                    sa.Column(
                        'hashed_password',
                        sa.String(255),
                        nullable=False,
                        comment='Хешированный пароль'
                    ),
                    sa.Column(
                        'full_name',
                        sa.String(100),
                        nullable=True,
                        comment='Полное имя'
                    ),
                    sa.Column(
                        'bio',
                        sa.Text(),
                        nullable=True,
                        comment='Биография пользователя'
                    ),
                    sa.Column(
                        'email_verified',
                        sa.Boolean(),
                        nullable=False,
                        comment='Подтвержден ли email'
                    ),
                    sa.Column(
                        'verification_token',
                        sa.String(255),
                        nullable=True,
                        comment='Токен для подтверждения email'
                    ),
                    sa.Column(
                        'verification_expires_at',
                        sa.DateTime(timezone=True),
                        nullable=True,
                        comment='Время истечения токена верификации'
                    ),
                    sa.Column(
                        'password_reset_token',
                        sa.String(255),
                        nullable=True,
                        comment='Токен для сброса пароля'
                    ),
                    sa.Column(
                        'password_reset_expires_at',
                        sa.DateTime(timezone=True),
                        nullable=True,
                        comment='Время истечения токена сброса пароля'
                    ),
                    sa.Column(
                        'last_login',
                        sa.DateTime(timezone=True),
                        nullable=True,
                        comment='Последний вход в систему'
                    ),
                    sa.Column(
                        'login_count',
                        sa.Integer(),
                        nullable=False,
                        comment='Количество входов в систему'
                    ),
                    sa.Column(
                        'is_active',
                        sa.Boolean(),
                        nullable=False,
                        comment='Активна ли запись'
                    ),
                    sa.Column(
                        'id',
                        sa.UUID(),
                        nullable=False,
                        comment='Уникальный идентификатор'
                    ),
                    sa.Column(
                        'created_at',
                        sa.DateTime(timezone=True),
                        server_default=sa.text('now()'),
                        nullable=False,
                        comment='Время создания записи'
                    ),
                    sa.Column(
                        'updated_at',
                        sa.DateTime(timezone=True),
                        server_default=sa.text('now()'),
                        nullable=True,
                        comment='Время последнего обновления'
                    ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(
        op.f('ix_users_email'),
        'users',
        ['email'],
        unique=True
    )
    op.create_index(
        op.f('ix_users_id'),
        'users', ['id'],
        unique=False
    )
    op.create_index(
        op.f('ix_users_user_name'),
        'users',
        ['user_name'],
        unique=True
    )

    # СОЗДАЕМ ТАБЛИЦУ LOGINATTEMPTS #############
    op.create_table('loginattempts',
                    sa.Column(
                        'user_id',
                        sa.UUID(),
                        nullable=True,
                        comment='ID пользователя'
                    ),
                    sa.Column(
                        'email',
                        sa.String(100),
                        nullable=False,
                        comment='Email, с которого была попытка входа'
                    ),
                    sa.Column(
                        'ip_address',
                        sa.String(45),
                        nullable=False,
                        comment='IP адрес'
                    ),
                    sa.Column(
                        'user_agent',
                        sa.String(500),
                        nullable=True,
                        comment='User Agent браузера'
                    ),
                    sa.Column(
                        'is_successful',
                        sa.Boolean(),
                        nullable=False,
                        comment='Успешна ли попытка'
                    ),
                    sa.Column(
                        'failure_reason',
                        sa.String(100),
                        nullable=True,
                        comment='Причина неудачи'
                    ),
                    sa.Column(
                        'is_active',
                        sa.Boolean(),
                        nullable=False,
                        comment='Активна ли запись'
                    ),
                    sa.Column(
                        'id',
                        sa.UUID(),
                        nullable=False,
                        comment='Уникальный идентификатор'
                    ),
                    sa.Column(
                        'created_at',
                        sa.DateTime(timezone=True),
                        server_default=sa.text('now()'),
                        nullable=False,
                        comment='Время создания'
                    ),
                    sa.Column(
                        'updated_at',
                        sa.DateTime(timezone=True),
                        server_default=sa.text('now()'),
                        nullable=True,
                        comment='Время обновления'
                    ),
                    sa.ForeignKeyConstraint(
                        ['user_id'],
                        ['users.id'],
                        ondelete='CASCADE'
                    ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(
        op.f('ix_loginattempts_email'),
        'loginattempts',
        ['email'],
        unique=False
    )
    op.create_index(
        op.f('ix_loginattempts_id'),
        'loginattempts',
        ['id'],
        unique=False
    )
    op.create_index(
        op.f('ix_loginattempts_user_id'),
        'loginattempts',
        ['user_id'],
        unique=False
    )

    # СОЗДАЕМ ТАБЛИЦУ REFREHTOKENS #############
    op.create_table('refreshtokens',
                    sa.Column(
                        'user_id',
                        sa.UUID(),
                        nullable=False,
                        comment='ID пользователя'
                    ),
                    sa.Column(
                        'token',
                        sa.String(255),
                        nullable=False,
                        comment='Значение токена'
                    ),
                    sa.Column(
                        'is_revoked',
                        sa.Boolean(),
                        nullable=False,
                        comment='Отозван ли токен'
                    ),
                    sa.Column(
                        'expires_at',
                        sa.DateTime(timezone=True),
                        nullable=False,
                        comment='Время истечения'
                    ),
                    sa.Column(
                        'is_active',
                        sa.Boolean(),
                        nullable=False,
                        comment='Активна ли запись'
                    ),
                    sa.Column(
                        'id',
                        sa.UUID(),
                        nullable=False,
                        comment='Уникальный идентификатор'
                    ),
                    sa.Column(
                        'created_at',
                        sa.DateTime(timezone=True),
                        server_default=sa.text('now()'),
                        nullable=False,
                        comment='Время создания'
                    ),
                    sa.Column(
                        'updated_at',
                        sa.DateTime(timezone=True),
                        server_default=sa.text('now()'),
                        nullable=True,
                        comment='Время обновления'
                    ),
                    sa.ForeignKeyConstraint(
                        ['user_id'],
                        ['users.id'],
                        ondelete='CASCADE'
                    ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(
        op.f('ix_refreshtokens_id'),
        'refreshtokens',
        ['id'],
        unique=False
    )
    op.create_index(
        op.f('ix_refreshtokens_token'),
        'refreshtokens',
        ['token'],
        unique=True
    )
    op.create_index(
        op.f('ix_refreshtokens_user_id'),
        'refreshtokens',
        ['user_id'],
        unique=False
    )

    # СОЗДАЕМ ТАБЛИЦУ USER_ROLES (M:N) #############
    op.create_table('user_roles',
                    sa.Column(
                        'user_id',
                        sa.UUID(),
                        nullable=False,
                        comment='ID пользователя'
                    ),
                    sa.Column(
                        'role_id',
                        sa.UUID(),
                        nullable=False,
                        comment='ID роли'
                    ),
                    sa.ForeignKeyConstraint(
                        ['role_id'],
                        ['rolemodel.id'],
                        ondelete='CASCADE'
                    ),
                    sa.ForeignKeyConstraint(
                        ['user_id'],
                        ['users.id'],
                        ondelete='CASCADE'
                    ),
                    sa.PrimaryKeyConstraint('user_id', 'role_id')
                    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table('user_roles')
    op.drop_index(
        op.f('ix_refreshtokens_user_id'),
        table_name='refreshtokens'
    )
    op.drop_index(
        op.f('ix_refreshtokens_token'),
        table_name='refreshtokens'
    )
    op.drop_index(
        op.f('ix_refreshtokens_id'),
        table_name='refreshtokens'
    )
    op.drop_table('refreshtokens')
    op.drop_index(
        op.f('ix_loginattempts_user_id'),
        table_name='loginattempts'
    )
    op.drop_index(
        op.f('ix_loginattempts_id'),
        table_name='loginattempts'
    )
    op.drop_index(
        op.f('ix_loginattempts_email'),
        table_name='loginattempts'
    )
    op.drop_table('loginattempts')
    op.drop_index(
        op.f('ix_users_user_name'),
        table_name='users'
    )
    op.drop_index(
        op.f('ix_users_id'),
        table_name='users'
    )
    op.drop_index(
        op.f('ix_users_email'),
        table_name='users'
    )
    op.drop_table('users')
    op.drop_index(
        op.f('ix_rolemodel_id'),
        table_name='rolemodel'
    )
    op.drop_table('rolemodel')
