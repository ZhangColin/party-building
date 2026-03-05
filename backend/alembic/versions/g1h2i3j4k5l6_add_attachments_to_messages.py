"""add_attachments_to_messages

Revision ID: g1h2i3j4k5l6
Revises: f1g2h3i4j5k6
Create Date: 2026-03-05 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g1h2i3j4k5l6'
down_revision: Union[str, Sequence[str], None] = 'f1g2h3i4j5k6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加 attachments 字段到 messages 表，支持聊天附件（本地文件、知识库、党建活动）"""
    # 添加 attachments 字段
    # 使用 TEXT 类型存储 JSON 字符串
    # 格式: [{"id": "...", "name": "文件名", "type": "temp|knowledge|party", "size": 123}]
    op.add_column('messages', sa.Column(
        'attachments',
        sa.Text(),
        nullable=True,
        comment='附件列表JSON字符串（本地文件、知识库、党建活动）'
    ))


def downgrade() -> None:
    """移除 attachments 字段"""
    op.drop_column('messages', 'attachments')
