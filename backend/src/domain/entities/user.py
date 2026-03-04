"""
User领域实体

User表示系统中的用户，包含业务规则和领域逻辑
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    用户实体

    Attributes:
        id: 用户唯一标识（UUID字符串）
        username: 用户名
        email: 邮箱地址
        is_admin: 是否为管理员
        created_at: 创建时间
    """
    id: str
    username: str
    email: str
    is_admin: bool
    created_at: datetime

    def can_access_tool(self, tool_id: str) -> bool:
        """
        检查用户是否可以访问指定工具

        业务规则：
        - 管理员可以访问所有工具
        - 普通用户当前可以访问所有工具（临时实现）
          TODO: 后续需要实现基于用户角色和工具可见性的权限控制

        Args:
            tool_id: 工具ID

        Returns:
            bool: 是否可以访问
        """
        # 管理员可以访问所有工具
        if self.is_admin:
            return True

        # TODO: 实现基于用户角色的权限控制
        # 当前临时实现：所有普通用户可以访问所有工具
        return True

    def is_premium_user(self) -> bool:
        """
        检查是否为付费用户

        Returns:
            bool: 是否为付费用户
        """
        # TODO: 实现付费用户逻辑
        return False

    @classmethod
    def create_new(cls, username: str, email: str, created_at: Optional[datetime] = None) -> "User":
        """
        创建新用户（工厂方法）

        Args:
            username: 用户名
            email: 邮箱
            created_at: 创建时间（可选，默认使用当前时间）

        Returns:
            User: 新用户实例
        """
        return cls(
            id="0",  # 数据库生成UUID
            username=username,
            email=email,
            is_admin=False,
            created_at=created_at or datetime.now()
        )
