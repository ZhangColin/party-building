"""
Session领域实体（临时占位）"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Session:
    """会话实体（临时）"""
    id: str
    user_id: str
    tool_id: str
    title: str
    created_at: datetime
