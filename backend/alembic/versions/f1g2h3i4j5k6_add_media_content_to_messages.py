"""add_media_content_to_messages

Revision ID: f1g2h3i4j5k6
Revises: e1f2g3h4i5j6
Create Date: 2026-01-23 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1g2h3i4j5k6'
down_revision: Union[str, Sequence[str], None] = 'e1f2g3h4i5j6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加 media_content 字段到 messages 表，支持多模态消息（图片、音频、视频）"""
    # 添加 media_content 字段
    # 使用 TEXT 类型存储 JSON 字符串
    # 格式: {"content_type": "image", "media_urls": [...], "metadata": {...}}
    op.add_column('messages', sa.Column(
        'media_content', 
        sa.Text(), 
        nullable=True,
        comment='多模态内容JSON字符串（图片、音频、视频等）'
    ))


def downgrade() -> None:
    """移除 media_content 字段"""
    op.drop_column('messages', 'media_content')
