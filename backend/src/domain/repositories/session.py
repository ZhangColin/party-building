"""
会话仓储接口
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.session import Session


class SessionRepository(ABC):
    """会话仓储接口"""

    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[Session]:
        """根据ID获取会话"""
        pass

    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[Session]:
        """获取用户的会话列表"""
        pass

    @abstractmethod
    async def create(self, session: Session) -> Session:
        """创建会话"""
        pass

    @abstractmethod
    async def update(self, session: Session) -> Session:
        """更新会话"""
        pass

    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """删除会话"""
        pass
