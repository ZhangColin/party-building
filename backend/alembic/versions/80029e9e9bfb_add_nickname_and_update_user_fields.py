"""add_nickname_and_update_user_fields

Revision ID: 80029e9e9bfb
Revises: 9ccc0f59aba1
Create Date: 2026-01-03 14:15:59.417116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80029e9e9bfb'
down_revision: Union[str, Sequence[str], None] = '9ccc0f59aba1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加 nickname 字段，修改 username 和 email 字段"""
    # 1. 添加 nickname 字段
    op.add_column('users', sa.Column('nickname', sa.String(50), nullable=True))
    
    # 2. 为 username 创建唯一索引（如果不存在）
    # 先检查索引是否存在，如果不存在则创建
    try:
        op.create_index('ix_users_username', 'users', ['username'], unique=True)
    except Exception:
        # 索引可能已存在，忽略错误
        pass
    
    # 3. 修改 email 字段为 nullable（保持唯一索引）
    # 在 MySQL 中，需要先删除唯一索引，修改字段，再重新创建唯一索引
    op.drop_index('ix_users_email', table_name='users')
    op.alter_column('users', 'email',
                    existing_type=sa.String(255),
                    nullable=True,
                    existing_nullable=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    """回滚修改"""
    # 删除 nickname 字段
    op.drop_column('users', 'nickname')
    
    # 删除 username 唯一索引
    op.drop_index('ix_users_username', table_name='users')
    
    # 恢复 email 字段为 not null
    op.drop_index('ix_users_email', table_name='users')
    op.alter_column('users', 'email',
                    existing_type=sa.String(255),
                    nullable=False,
                    existing_nullable=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
