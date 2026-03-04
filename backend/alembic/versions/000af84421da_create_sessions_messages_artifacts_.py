"""create_sessions_messages_artifacts_tables

Revision ID: 000af84421da
Revises: 4a7fcb1183df
Create Date: 2026-01-03 20:14:39.657191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000af84421da'
down_revision: Union[str, Sequence[str], None] = '4a7fcb1183df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 sessions、messages、artifacts 表"""
    # 创建 sessions 表
    op.create_table(
        'sessions',
        sa.Column('session_id', sa.CHAR(length=36), nullable=False),
        sa.Column('user_id', sa.CHAR(length=36), nullable=False),
        sa.Column('tool_id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_id')
    )
    op.create_index('idx_user_id', 'sessions', ['user_id'])
    op.create_index('idx_tool_id', 'sessions', ['tool_id'])
    op.create_index('idx_user_tool', 'sessions', ['user_id', 'tool_id'])
    op.create_index('idx_updated_at', 'sessions', ['updated_at'])
    
    # 创建 messages 表
    op.create_table(
        'messages',
        sa.Column('message_id', sa.CHAR(length=36), nullable=False),
        sa.Column('session_id', sa.CHAR(length=36), nullable=False),
        sa.Column('role', sa.Enum('user', 'assistant', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('message_id')
    )
    op.create_index('idx_session_id', 'messages', ['session_id'])
    op.create_index('idx_created_at', 'messages', ['created_at'])
    
    # 创建 artifacts 表
    op.create_table(
        'artifacts',
        sa.Column('artifact_id', sa.CHAR(length=36), nullable=False),
        sa.Column('message_id', sa.CHAR(length=36), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['message_id'], ['messages.message_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('artifact_id')
    )
    op.create_index('idx_message_id', 'artifacts', ['message_id'])


def downgrade() -> None:
    """删除 sessions、messages、artifacts 表"""
    op.drop_index('idx_message_id', table_name='artifacts')
    op.drop_table('artifacts')
    op.drop_index('idx_created_at', table_name='messages')
    op.drop_index('idx_session_id', table_name='messages')
    op.drop_table('messages')
    op.drop_index('idx_updated_at', table_name='sessions')
    op.drop_index('idx_user_tool', table_name='sessions')
    op.drop_index('idx_tool_id', table_name='sessions')
    op.drop_index('idx_user_id', table_name='sessions')
    op.drop_table('sessions')
