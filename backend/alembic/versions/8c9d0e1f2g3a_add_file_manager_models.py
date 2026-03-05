"""添加文件管理模型

Revision ID: 8c9d0e1f2g3a
Revises: 7b840677f9ce
Create Date: 2026-03-05 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '8c9d0e1f2g3a'
down_revision: Union[str, Sequence[str], None] = '7b840677f9ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加文件管理相关表"""
    # 先删除旧的知识库表（如果存在）
    # 使用 batch_alter_table 以避免外键约束问题
    try:
        op.drop_table('knowledge_documents')
    except Exception:
        pass
    try:
        op.drop_table('knowledge_categories')
    except Exception:
        pass

    # 创建知识库目录表（支持树形结构）
    op.create_table('knowledge_categories',
        sa.Column('id', mysql.CHAR(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='目录名称'),
        sa.Column('parent_id', mysql.CHAR(length=36), nullable=True, comment='父目录ID'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0', comment='排序'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['parent_id'], ['knowledge_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_knowledge_category_parent', 'knowledge_categories', ['parent_id'], unique=False)
    op.create_index('idx_knowledge_category_order', 'knowledge_categories', ['order'], unique=False)

    # 创建知识库文档表（支持双轨存储）
    op.create_table('knowledge_documents',
        sa.Column('id', mysql.CHAR(length=36), nullable=False),
        sa.Column('category_id', mysql.CHAR(length=36), nullable=False, comment='所属目录ID'),
        sa.Column('filename', sa.String(length=255), nullable=False, comment='文件名'),
        sa.Column('original_filename', sa.String(length=255), nullable=False, comment='原始文件名'),
        sa.Column('original_path', sa.String(length=500), nullable=True, comment='原文件存储路径'),
        sa.Column('markdown_path', sa.String(length=500), nullable=True, comment='Markdown文件路径'),
        sa.Column('file_type', sa.String(length=20), nullable=False, comment='文件类型'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='文件大小（字节）'),
        sa.Column('uploaded_by', mysql.CHAR(length=36), nullable=True, comment='上传者ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['category_id'], ['knowledge_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_knowledge_doc_category', 'knowledge_documents', ['category_id'], unique=False)
    op.create_index('idx_knowledge_doc_type', 'knowledge_documents', ['file_type'], unique=False)

    # 创建党建活动目录表（支持树形结构）
    op.create_table('party_activity_categories',
        sa.Column('id', mysql.CHAR(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='目录名称'),
        sa.Column('parent_id', mysql.CHAR(length=36), nullable=True, comment='父目录ID'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0', comment='排序'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['parent_id'], ['party_activity_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_party_activity_category_parent', 'party_activity_categories', ['parent_id'], unique=False)
    op.create_index('idx_party_activity_category_order', 'party_activity_categories', ['order'], unique=False)

    # 创建党建活动文档表（支持双轨存储）
    op.create_table('party_activity_documents',
        sa.Column('id', mysql.CHAR(length=36), nullable=False),
        sa.Column('category_id', mysql.CHAR(length=36), nullable=False, comment='所属目录ID'),
        sa.Column('filename', sa.String(length=255), nullable=False, comment='文件名'),
        sa.Column('original_filename', sa.String(length=255), nullable=False, comment='原始文件名'),
        sa.Column('original_path', sa.String(length=500), nullable=True, comment='原文件存储路径'),
        sa.Column('markdown_path', sa.String(length=500), nullable=True, comment='Markdown文件路径'),
        sa.Column('file_type', sa.String(length=20), nullable=False, comment='文件类型'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='文件大小（字节）'),
        sa.Column('uploaded_by', mysql.CHAR(length=36), nullable=True, comment='上传者ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['category_id'], ['party_activity_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_party_activity_doc_category', 'party_activity_documents', ['category_id'], unique=False)
    op.create_index('idx_party_activity_doc_type', 'party_activity_documents', ['file_type'], unique=False)


def downgrade() -> None:
    """回滚文件管理相关表"""
    op.drop_index('idx_party_activity_doc_type', table_name='party_activity_documents')
    op.drop_index('idx_party_activity_doc_category', table_name='party_activity_documents')
    op.drop_table('party_activity_documents')

    op.drop_index('idx_party_activity_category_order', table_name='party_activity_categories')
    op.drop_index('idx_party_activity_category_parent', table_name='party_activity_categories')
    op.drop_table('party_activity_categories')

    op.drop_index('idx_knowledge_doc_type', table_name='knowledge_documents')
    op.drop_index('idx_knowledge_doc_category', table_name='knowledge_documents')
    op.drop_table('knowledge_documents')

    op.drop_index('idx_knowledge_category_order', table_name='knowledge_categories')
    op.drop_index('idx_knowledge_category_parent', table_name='knowledge_categories')
    op.drop_table('knowledge_categories')
