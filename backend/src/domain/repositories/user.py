"""
用户仓储接口
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.user import User


class UserRepository(ABC):
    """用户仓储接口"""

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        """创建用户"""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """更新用户"""
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> None:
        """删除用户"""
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """获取用户列表"""
        pass
