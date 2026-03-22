"""Create users and related tables

Revision ID: 001
Revises:
Create Date: 2026-03-22

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Таблица users
    op.create_table('users',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('user_name', sa.String(50), nullable=False),
                    sa.Column('email', sa.String(100), nullable=False),
                    sa.Column('hashed_password', sa.String(
                        255), nullable=False),
                    sa.Column('full_name', sa.String(100), nullable=True),
                    sa.Column('bio', sa.Text(), nullable=True),
                    sa.Column('email_verified', sa.Boolean(),
                              nullable=False, server_default='false'),
                    sa.Column('verification_token',
                              sa.String(255), nullable=True),
                    sa.Column('verification_expires_at', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.Column('password_reset_token',
                              sa.String(255), nullable=True),
                    sa.Column('password_reset_expires_at',
                              sa.DateTime(timezone=True), nullable=True),
                    sa.Column('last_login', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.Column('login_count', sa.Integer(),
                              nullable=False, server_default='0'),
                    sa.Column('role_name', sa.String(50),
                              nullable=False, server_default='user'),
                    sa.Column('is_active', sa.Boolean(),
                              nullable=False, server_default='true'),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_name'),
                    sa.UniqueConstraint('email')
                    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_role_name', 'users', ['role_name'])

    # Таблица refreshtokens
    op.create_table('refreshtokens',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('user_id', sa.UUID(), nullable=False),
                    sa.Column('token', sa.String(255), nullable=False),
                    sa.Column('is_revoked', sa.Boolean(),
                              nullable=False, server_default='false'),
                    sa.Column('expires_at', sa.DateTime(
                        timezone=True), nullable=False),
                    sa.Column('is_active', sa.Boolean(),
                              nullable=False, server_default='true'),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('token')
                    )
    op.create_index('ix_refreshtokens_id', 'refreshtokens', ['id'])
    op.create_index('ix_refreshtokens_user_id', 'refreshtokens', ['user_id'])

    # Таблица loginattempts
    op.create_table('loginattempts',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('user_id', sa.UUID(), nullable=True),
                    sa.Column('email', sa.String(100), nullable=False),
                    sa.Column('ip_address', sa.String(45), nullable=False),
                    sa.Column('user_agent', sa.String(500), nullable=True),
                    sa.Column('is_successful', sa.Boolean(), nullable=False),
                    sa.Column('failure_reason', sa.String(100), nullable=True),
                    sa.Column('is_active', sa.Boolean(),
                              nullable=False, server_default='true'),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('ix_loginattempts_id', 'loginattempts', ['id'])
    op.create_index('ix_loginattempts_email', 'loginattempts', ['email'])


def downgrade() -> None:
    op.drop_table('loginattempts')
    op.drop_table('refreshtokens')
    op.drop_table('users')
