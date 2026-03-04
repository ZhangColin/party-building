"""
MessageRole值对象单元测试
"""
import pytest
from src.domain.value_objects.message_role import MessageRole


class TestMessageRole:
    """MessageRole测试类"""

    def test_user_role(self):
        """测试用户角色"""
        role = MessageRole.USER

        assert role == "user"
        assert role.is_user_message() is True
        assert role.is_assistant_message() is False
        assert role.is_system_message() is False

    def test_assistant_role(self):
        """测试助手角色"""
        role = MessageRole.ASSISTANT

        assert role == "assistant"
        assert role.is_user_message() is False
        assert role.is_assistant_message() is True
        assert role.is_system_message() is False

    def test_system_role(self):
        """测试系统角色"""
        role = MessageRole.SYSTEM

        assert role == "system"
        assert role.is_user_message() is False
        assert role.is_assistant_message() is False
        assert role.is_system_message() is True

    def test_role_equality(self):
        """测试角色比较"""
        assert MessageRole.USER == MessageRole.USER
        assert MessageRole.USER != MessageRole.ASSISTANT
