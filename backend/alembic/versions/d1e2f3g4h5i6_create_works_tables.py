"""create works tables

Revision ID: d1e2f3g4h5i6
Revises: b1c2d3e4f5g6
Create Date: 2026-01-11 22:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd1e2f3g4h5i6'
down_revision = 'b1c2d3e4f5g6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建作品分类表
    op.create_table(
        'work_categories',
        sa.Column('id', sa.String(36), primary_key=True, comment='分类ID（UUID）'),
        sa.Column('name', sa.String(50), nullable=False, unique=True, comment='分类名称'),
        sa.Column('icon', sa.String(50), nullable=True, comment='分类图标（heroicons名称）'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0', comment='排序顺序'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='作品分类表'
    )
    
    # 创建索引
    op.create_index('idx_order', 'work_categories', ['order'])
    
    # 创建作品表
    op.create_table(
        'works',
        sa.Column('id', sa.String(36), primary_key=True, comment='作品ID（UUID）'),
        sa.Column('name', sa.String(100), nullable=False, comment='作品名称'),
        sa.Column('description', sa.String(200), nullable=False, comment='作品描述'),
        sa.Column('category_id', sa.String(36), nullable=False, comment='所属分类ID'),
        sa.Column('icon', sa.String(50), nullable=True, comment='图标标识（heroicons名称）'),
        sa.Column('html_path', sa.String(255), nullable=False, comment='HTML文件路径（相对于static目录）'),
        sa.Column('order', sa.Integer(), nullable=False, server_default='0', comment='排序顺序'),
        sa.Column('visible', sa.Boolean(), nullable=False, server_default='1', comment='是否可见'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='作品表'
    )
    
    # 创建外键
    op.create_foreign_key(
        'fk_works_category_id',
        'works', 'work_categories',
        ['category_id'], ['id'],
        ondelete='RESTRICT'
    )
    
    # 创建索引
    op.create_index('idx_category_order', 'works', ['category_id', 'order'])
    op.create_index('idx_visible', 'works', ['visible'])
    
    # 插入初始分类数据
    op.execute("""
        INSERT INTO work_categories (id, name, icon, `order`) VALUES
        ('creative-design', '创意设计', 'sparkles', 1),
        ('data-visualization', '数据可视化', 'chart-bar', 2),
        ('interactive-animation', '交互动画', 'cursor-arrow-rays', 3)
    """)


def downgrade() -> None:
    # 删除作品表（先删除，因为有外键依赖）
    op.drop_table('works')
    
    # 删除作品分类表
    op.drop_table('work_categories')

