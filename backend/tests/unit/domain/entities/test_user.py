# -*- coding: utf-8 -*-
"""
User领域实体单元测试
"""
import pytest
from datetime import datetime
from src.domain.entities.user import User


@pytest.mark.unit
class TestUser:
    """User实体测试类"""

    def test_create_new_user(self):
        """测试工厂方法创建用户"""
        user = User.create_new(
            username="testuser",
            email="test@example.com"
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_admin is False
        assert isinstance(user.created_at, datetime)
        assert user.id == "0"  # 数据库生成UUID

    def test_create_new_user_with_custom_created_at(self):
        """测试使用自定义创建时间创建用户"""
        custom_time = datetime(2026, 2, 28, 12, 0, 0)
        user = User.create_new(
            username="testuser",
            email="test@example.com",
            created_at=custom_time
        )

        assert user.created_at == custom_time

    def test_admin_can_access_all_tools(self):
        """测试管理员可以访问所有工具"""
        admin = User.create_new("admin", "admin@example.com")
        admin.is_admin = True

        assert admin.can_access_tool("any-tool") is True
        assert admin.can_access_tool("restricted-tool") is True
        assert admin.can_access_tool("admin-only-tool") is True

    def test_normal_user_can_access_tools(self):
        """测试普通用户可以访问工具（临时实现）"""
        user = User.create_new("user", "user@example.com")

        # 当前临时实现：普通用户可以访问所有工具
        assert user.can_access_tool("any-tool") is True
        assert user.can_access_tool("some-tool") is True

    def test_is_premium_user_returns_false(self):
        """测试付费用户检查（待实现功能）"""
        user = User.create_new("user", "user@example.com")

        # TODO: 实现付费用户逻辑
        assert user.is_premium_user() is False

    def test_admin_is_premium_user_also_false(self):
        """测试管理员也不是付费用户（待实现功能）"""
        admin = User.create_new("admin", "admin@example.com")
        admin.is_admin = True

        # TODO: 实现付费用户逻辑
        assert admin.is_premium_user() is False

    def test_user_attributes(self):
        """测试用户属性设置"""
        user = User(
            id="123",
            username="testuser",
            email="test@example.com",
            is_admin=False,
            created_at=datetime.now()
        )

        assert user.id == "123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_admin is False
