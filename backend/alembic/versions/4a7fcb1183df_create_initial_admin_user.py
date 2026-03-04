"""create_initial_admin_user

Revision ID: 4a7fcb1183df
Revises: 80029e9e9bfb
Create Date: 2026-01-03 14:45:45.013659

"""
from typing import Sequence, Union
import uuid
import bcrypt
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a7fcb1183df'
down_revision: Union[str, Sequence[str], None] = '80029e9e9bfb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建系统初始化用户"""
    # 检查用户是否已存在
    connection = op.get_bind()
    result = connection.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE username = :username OR email = :email OR phone = :phone"),
        {"username": "colin", "email": "zhangjinhua@aieducenter.com", "phone": "18001828301"}
    )
    count = result.scalar()
    
    if count == 0:
        # 用户不存在，创建初始化用户
        user_id = str(uuid.uuid4())
        password_hash = bcrypt.hashpw("Hcy@2026".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_at = datetime.now()
        
        connection.execute(
            sa.text("""
                INSERT INTO users (user_id, username, nickname, email, phone, password_hash, avatar, created_at)
                VALUES (:user_id, :username, :nickname, :email, :phone, :password_hash, :avatar, :created_at)
            """),
            {
                "user_id": user_id,
                "username": "colin",
                "nickname": "文野",
                "email": "zhangjinhua@aieducenter.com",
                "phone": "18001828301",
                "password_hash": password_hash,
                "avatar": None,
                "created_at": created_at
            }
        )


def downgrade() -> None:
    """删除系统初始化用户"""
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM users WHERE username = :username"),
        {"username": "colin"}
    )
