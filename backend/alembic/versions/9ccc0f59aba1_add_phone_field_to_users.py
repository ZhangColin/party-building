"""add_phone_field_to_users

Revision ID: 9ccc0f59aba1
Revises: aa4b486d758f
Create Date: 2026-01-03 13:44:07.486634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ccc0f59aba1'
down_revision: Union[str, Sequence[str], None] = 'aa4b486d758f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加 phone 字段到 users 表"""
    # 添加 phone 字段
    op.add_column('users', sa.Column('phone', sa.String(11), nullable=True))
    # 创建 phone 唯一索引
    op.create_index('ix_users_phone', 'users', ['phone'], unique=True)


def downgrade() -> None:
    """移除 phone 字段"""
    # 删除索引
    op.drop_index('ix_users_phone', table_name='users')
    # 删除字段
    op.drop_column('users', 'phone')
