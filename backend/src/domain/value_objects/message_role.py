"""
MessageRole值对象

表示对话中消息的角色（用户/助手/系统）
"""
from enum import Enum


class MessageRole(str, Enum):
    """
    消息角色枚举

    Values:
        USER: 用户消息
        ASSISTANT: AI助手消息
        SYSTEM: 系统提示词消息
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

    def is_user_message(self) -> bool:
        """检查是否为用户消息"""
        return self == MessageRole.USER

    def is_assistant_message(self) -> bool:
        """检查是否为助手消息"""
        return self == MessageRole.ASSISTANT

    def is_system_message(self) -> bool:
        """检查是否为系统消息"""
        return self == MessageRole.SYSTEM
