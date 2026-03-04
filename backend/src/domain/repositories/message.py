"""
消息仓储接口
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.message import Message


class MessageRepository(ABC):
    """消息仓储接口"""

    @abstractmethod
    async def get_by_id(self, message_id: str) -> Optional[Message]:
        """根据ID获取消息"""
        pass

    @abstractmethod
    async def get_by_session_id(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Message]:
        """获取会话的消息列表"""
        pass

    @abstractmethod
    async def create(self, message: Message) -> Message:
        """创建消息"""
        pass

    @abstractmethod
    async def create_batch(self, messages: list[Message]) -> list[Message]:
        """批量创建消息"""
        pass

    @abstractmethod
    async def delete(self, message_id: str) -> None:
        """删除消息"""
        pass

    @abstractmethod
    async def delete_by_session_id(self, session_id: str) -> None:
        """删除会话的所有消息"""
        pass
