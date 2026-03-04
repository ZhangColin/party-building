"""
Message领域实体

Message表示对话中的一条消息
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.entities.artifact import Artifact
from src.domain.value_objects.message_role import MessageRole


@dataclass
class Message:
    """
    消息实体

    Attributes:
        id: 消息唯一标识（UUID字符串）
        session_id: 所属会话ID
        role: 消息角色（user/assistant/system）
        content: 消息内容
        artifact: 可选的成果物（AI生成的内容）
        created_at: 创建时间
    """
    id: str
    session_id: str
    role: MessageRole
    content: str
    artifact: Optional[Artifact]
    created_at: datetime

    def is_from_user(self) -> bool:
        """检查消息是否来自用户"""
        return self.role.is_user_message()

    def is_from_assistant(self) -> bool:
        """检查消息是否来自助手"""
        return self.role.is_assistant_message()

    def is_system_prompt(self) -> bool:
        """检查是否为系统提示词"""
        return self.role.is_system_message()

    def has_artifact(self) -> bool:
        """检查是否包含成果物"""
        return self.artifact is not None

    def get_content_length(self) -> int:
        """获取消息内容长度"""
        return len(self.content)

    @classmethod
    def create_user_message(cls, session_id: str, content: str) -> "Message":
        """
        创建用户消息（工厂方法）

        Args:
            session_id: 会话ID
            content: 消息内容

        Returns:
            Message: 用户消息实例
        """
        return cls(
            id="0",  # 数据库生成
            session_id=session_id,
            role=MessageRole.USER,
            content=content,
            artifact=None,
            created_at=datetime.now()
        )

    @classmethod
    def create_assistant_message(
        cls,
        session_id: str,
        content: str,
        artifact: Optional[Artifact] = None
    ) -> "Message":
        """
        创建助手消息（工厂方法）

        Args:
            session_id: 会话ID
            content: 消息内容
            artifact: 可选的成果物

        Returns:
            Message: 助手消息实例
        """
        return cls(
            id="0",  # 数据库生成
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=content,
            artifact=artifact,
            created_at=datetime.now()
        )
