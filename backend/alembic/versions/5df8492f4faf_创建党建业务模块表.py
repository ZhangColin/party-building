"""创建党建业务模块表

Revision ID: 5df8492f4faf
Revises: f1g2h3i4j5k6
Create Date: 2026-03-05 06:16:21.201599

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5df8492f4faf'
down_revision: Union[str, Sequence[str], None] = 'f1g2h3i4j5k6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建党建业务模块表"""
    # 创建党员信息表
    op.create_table('party_members',
        sa.Column('member_id', mysql.CHAR(length=36), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False, comment='姓名'),
        sa.Column('gender', sa.String(length=10), nullable=False, comment='性别'),
        sa.Column('birth_date', sa.Date(), nullable=False, comment='出生日期'),
        sa.Column('join_date', sa.Date(), nullable=False, comment='入党时间'),
        sa.Column('party_branch', sa.String(length=100), nullable=False, comment='所属党支部'),
        sa.Column('member_type', sa.String(length=50), nullable=False, server_default='正式党员', comment='党员类型'),
        sa.Column('phone', sa.String(length=20), nullable=True, comment='联系电话'),
        sa.Column('email', sa.String(length=100), nullable=True, comment='邮箱'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='正常', comment='状态'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.PrimaryKeyConstraint('member_id')
    )
    op.create_index('idx_party_member_branch', 'party_members', ['party_branch'], unique=False)
    op.create_index('idx_party_member_name', 'party_members', ['name'], unique=False)
    op.create_index('idx_party_member_status', 'party_members', ['status'], unique=False)

    # 创建组织生活记录表
    op.create_table('organization_lives',
        sa.Column('life_id', mysql.CHAR(length=36), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False, comment='活动类型'),
        sa.Column('title', sa.String(length=200), nullable=False, comment='活动主题'),
        sa.Column('activity_date', sa.DateTime(), nullable=False, comment='活动时间'),
        sa.Column('location', sa.String(length=200), nullable=True, comment='活动地点'),
        sa.Column('participants_count', sa.Integer(), nullable=False, server_default='0', comment='参与人数'),
        sa.Column('content', sa.Text(), nullable=True, comment='活动内容摘要'),
        sa.Column('organizer', sa.String(length=100), nullable=True, comment='组织者'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.PrimaryKeyConstraint('life_id')
    )
    op.create_index('idx_org_life_date', 'organization_lives', ['activity_date'], unique=False)
    op.create_index('idx_org_life_type', 'organization_lives', ['activity_type'], unique=False)

    # 创建党费记录表
    op.create_table('party_fees',
        sa.Column('fee_id', mysql.CHAR(length=36), nullable=False),
        sa.Column('member_id', mysql.CHAR(length=36), nullable=True, comment='党员ID'),
        sa.Column('member_name', sa.String(length=50), nullable=False, comment='党员姓名'),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='缴纳金额'),
        sa.Column('payment_date', sa.DateTime(), nullable=False, comment='缴纳时间'),
        sa.Column('payment_method', sa.String(length=50), nullable=False, server_default='现金', comment='缴纳方式'),
        sa.Column('fee_month', sa.String(length=7), nullable=False, comment='缴费月份'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='已缴', comment='状态'),
        sa.Column('remark', sa.String(length=500), nullable=True, comment='备注'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['member_id'], ['party_members.member_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('fee_id')
    )
    op.create_index('idx_party_fee_member', 'party_fees', ['member_id'], unique=False)
    op.create_index('idx_party_fee_month', 'party_fees', ['fee_month'], unique=False)
    op.create_index('idx_party_fee_status', 'party_fees', ['status'], unique=False)


def downgrade() -> None:
    """回滚党建业务模块表"""
    op.drop_index('idx_party_fee_status', table_name='party_fees')
    op.drop_index('idx_party_fee_month', table_name='party_fees')
    op.drop_index('idx_party_fee_member', table_name='party_fees')
    op.drop_table('party_fees')

    op.drop_index('idx_org_life_type', table_name='organization_lives')
    op.drop_index('idx_org_life_date', table_name='organization_lives')
    op.drop_table('organization_lives')

    op.drop_index('idx_party_member_status', table_name='party_members')
    op.drop_index('idx_party_member_name', table_name='party_members')
    op.drop_index('idx_party_member_branch', table_name='party_members')
    op.drop_table('party_members')
