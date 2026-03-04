"""add is_admin field to users

Revision ID: c1d2e3f4g5h6
Revises: b1c2d3e4f5g6
Create Date: 2026-01-11 10:00:00.000000

"""
from typing import Sequence, Union
import uuid
import bcrypt
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4g5h6'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5g6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加 is_admin 字段并创建管理员账号"""
    connection = op.get_bind()
    
    # 1. 添加 is_admin 字段（默认为 false）
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='0'))
    
    # 2. 创建索引
    op.create_index('idx_is_admin', 'users', ['is_admin'])
    
    # 3. 检查并创建管理员账号（admin / HcyAdmin@2026）
    result = connection.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE username = :username"),
        {"username": "admin"}
    )
    count = result.scalar()
    
    if count == 0:
        # 管理员账号不存在，创建
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw("HcyAdmin@2026".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_at = datetime.now()
        
        connection.execute(
            sa.text("""
                INSERT INTO users (user_id, username, nickname, email, phone, password_hash, avatar, is_admin, created_at)
                VALUES (:user_id, :username, :nickname, :email, :phone, :password_hash, :avatar, :is_admin, :created_at)
            """),
            {
                "user_id": user_id,
                "username": "admin",
                "nickname": "系统管理员",
                "email": "admin@example.com",
                "phone": None,
                "password_hash": password_hash,
                "avatar": None,
                "is_admin": True,
                "created_at": created_at
            }
        )
        print("✅ 管理员账号创建成功: admin / HcyAdmin@2026")
    else:
        # 管理员账号已存在，更新为管理员权限
        connection.execute(
            sa.text("UPDATE users SET is_admin = :is_admin WHERE username = :username"),
            {"is_admin": True, "username": "admin"}
        )
        print("✅ 管理员账号已存在，已更新权限")


def downgrade() -> None:
    """删除 is_admin 字段"""
    # 1. 删除索引
    op.drop_index('idx_is_admin', table_name='users')
    
    # 2. 删除字段
    op.drop_column('users', 'is_admin')
