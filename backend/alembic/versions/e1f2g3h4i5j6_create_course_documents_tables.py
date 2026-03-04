"""create course documents tables

Revision ID: e1f2g3h4i5j6
Revises: c1d2e3f4g5h6, d1e2f3g4h5i6
Create Date: 2026-01-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e1f2g3h4i5j6'
down_revision = ('c1d2e3f4g5h6', 'd1e2f3g4h5i6')  # Merge both branches
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建文档目录表
    op.create_table(
        'course_categories',
        sa.Column('id', sa.String(36), primary_key=True, comment='目录ID（UUID）'),
        sa.Column('name', sa.String(100), nullable=False, comment='目录名称'),
        sa.Column('parent_id', sa.String(36), nullable=True, comment='父目录ID（NULL表示根目录）'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0', comment='排序顺序'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='文档目录表'
    )
    
    # 创建自引用外键（支持多级目录）
    op.create_foreign_key(
        'fk_course_categories_parent_id',
        'course_categories', 'course_categories',
        ['parent_id'], ['id'],
        ondelete='RESTRICT'
    )
    
    # 创建索引
    op.create_index('idx_parent_order', 'course_categories', ['parent_id', 'order'])
    
    # 创建文档表
    op.create_table(
        'course_documents',
        sa.Column('id', sa.String(36), primary_key=True, comment='文档ID（UUID）'),
        sa.Column('title', sa.String(200), nullable=False, comment='文档标题'),
        sa.Column('summary', sa.String(500), nullable=False, comment='文档摘要'),
        sa.Column('file_path', sa.String(255), nullable=False, comment='Markdown文件路径（相对于static目录）'),
        sa.Column('category_id', sa.String(36), nullable=False, comment='所属目录ID'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0', comment='排序顺序'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='文档表'
    )
    
    # 创建外键
    op.create_foreign_key(
        'fk_course_documents_category_id',
        'course_documents', 'course_categories',
        ['category_id'], ['id'],
        ondelete='RESTRICT'
    )
    
    # 创建索引
    op.create_index('idx_category_order', 'course_documents', ['category_id', 'order'])
    
    # 插入初始目录数据（示例）
    op.execute("""
        INSERT INTO course_categories (id, name, parent_id, `order`) VALUES
        ('chapter-001', '第一章：AI基础', NULL, 1),
        ('chapter-002', '第二章：AI应用', NULL, 2),
        ('section-001', '1.1 什么是AI', 'chapter-001', 1),
        ('section-002', '1.2 AI的发展历史', 'chapter-001', 2)
    """)


def downgrade() -> None:
    # 删除文档表（先删除，因为有外键依赖）
    op.drop_table('course_documents')
    
    # 删除文档目录表
    op.drop_table('course_categories')

