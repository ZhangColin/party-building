"""create_common_tools_tables

Revision ID: b1c2d3e4f5g6
Revises: 000af84421da
Create Date: 2026-01-09 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, Sequence[str], None] = '000af84421da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 tool_categories 和 common_tools 表"""
    # 创建 tool_categories 表
    op.create_table(
        'tool_categories',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('idx_order', 'tool_categories', ['order'])
    
    # 创建 common_tools 表
    op.create_table(
        'common_tools',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=False),
        sa.Column('category_id', sa.String(length=36), nullable=False),
        sa.Column('type', sa.Enum('built_in', 'html', name='commontooltype'), nullable=False),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('html_path', sa.String(length=255), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('visible', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['tool_categories.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_category_id', 'common_tools', ['category_id'])
    op.create_index('idx_visible', 'common_tools', ['visible'])
    op.create_index('idx_category_order', 'common_tools', ['category_id', 'order'])
    
    # 插入初始数据
    from datetime import datetime
    now = datetime.now()
    
    # 插入工具分类
    op.bulk_insert(
        sa.table('tool_categories',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('icon', sa.String),
            sa.column('order', sa.Integer),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ),
        [
            {'id': 'doc-tools', 'name': '文档工具', 'icon': 'document-text', 'order': 1, 'created_at': now, 'updated_at': now},
            {'id': 'data-tools', 'name': '数据工具', 'icon': 'chart-bar', 'order': 2, 'created_at': now, 'updated_at': now}
        ]
    )
    
    # 插入常用工具
    op.bulk_insert(
        sa.table('common_tools',
            sa.column('id', sa.String),
            sa.column('name', sa.String),
            sa.column('description', sa.String),
            sa.column('category_id', sa.String),
            sa.column('type', sa.String),
            sa.column('icon', sa.String),
            sa.column('html_path', sa.String),
            sa.column('order', sa.Integer),
            sa.column('visible', sa.Boolean),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime)
        ),
        [
            {
                'id': 'markdown-editor',
                'name': 'Markdown编辑器',
                'description': '在线编辑Markdown文档，实时预览，支持导出Word/PDF',
                'category_id': 'doc-tools',
                'type': 'built_in',
                'icon': 'document-text',
                'html_path': None,
                'order': 1,
                'visible': True,
                'created_at': now,
                'updated_at': now
            }
        ]
    )


def downgrade() -> None:
    """删除 tool_categories 和 common_tools 表"""
    op.drop_index('idx_category_order', table_name='common_tools')
    op.drop_index('idx_visible', table_name='common_tools')
    op.drop_index('idx_category_id', table_name='common_tools')
    op.drop_table('common_tools')
    op.drop_index('idx_order', table_name='tool_categories')
    op.drop_table('tool_categories')
