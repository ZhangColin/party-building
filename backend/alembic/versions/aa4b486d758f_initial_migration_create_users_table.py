"""Initial migration: create users table

Revision ID: aa4b486d758f
Revises: 
Create Date: 2026-01-03 12:42:38.882669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.mysql import CHAR


# revision identifiers, used by Alembic.
revision: str = 'aa4b486d758f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 users 表"""
    op.create_table(
        'users',
        sa.Column('user_id', CHAR(36), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('avatar', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    # 创建 email 唯一索引
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    """删除 users 表"""
    # 删除索引
    op.drop_index('ix_users_email', table_name='users')
    # 删除表
    op.drop_table('users')
