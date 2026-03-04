"""
Message实体单元测试
"""
import pytest
from datetime import datetime
from src.domain.entities.message import Message
from src.domain.entities.artifact import Artifact
from src.domain.value_objects.message_role import MessageRole


class TestMessage:
    """Message实体测试类"""

    def test_message_attributes(self):
        """测试消息属性"""
        # Arrange
        created_at = datetime(2024, 1, 1, 12, 0, 0)
        artifact = Artifact(
            id="artifact-1",
            type="markdown",
            content="# Hello",
            created_at=created_at
        )

        message = Message(
            id="msg-1",
            session_id="session-1",
            role=MessageRole.ASSISTANT,
            content="Here's your lesson plan",
            artifact=artifact,
            created_at=created_at
        )

        # Assert
        assert message.id == "msg-1"
        assert message.session_id == "session-1"
        assert message.role == MessageRole.ASSISTANT
        assert message.content == "Here's your lesson plan"
        assert message.artifact == artifact
        assert message.created_at == created_at

    def test_is_from_user(self):
        """测试用户消息检查"""
        message = Message(
            id="msg-1",
            session_id="session-1",
            role=MessageRole.USER,
            content="Hello",
            artifact=None,
            created_at=datetime.now()
        )

        assert message.is_from_user() is True
        assert message.is_from_assistant() is False
        assert message.is_system_prompt() is False

    def test_is_from_assistant(self):
        """测试助手消息检查"""
        message = Message(
            id="msg-2",
            session_id="session-1",
            role=MessageRole.ASSISTANT,
            content="Hi there",
            artifact=None,
            created_at=datetime.now()
        )

        assert message.is_from_user() is False
        assert message.is_from_assistant() is True
        assert message.is_system_prompt() is False

    def test_has_artifact(self):
        """测试成果物检查"""
        artifact = Artifact(
            id="artifact-1",
            type="html",
            content="<div>Hello</div>",
            created_at=datetime.now()
        )

        message_with_artifact = Message(
            id="msg-1",
            session_id="session-1",
            role=MessageRole.ASSISTANT,
            content="Here's HTML",
            artifact=artifact,
            created_at=datetime.now()
        )

        message_without_artifact = Message(
            id="msg-2",
            session_id="session-1",
            role=MessageRole.USER,
            content="Hello",
            artifact=None,
            created_at=datetime.now()
        )

        assert message_with_artifact.has_artifact() is True
        assert message_without_artifact.has_artifact() is False

    def test_get_content_length(self):
        """测试内容长度计算"""
        message = Message(
            id="msg-1",
            session_id="session-1",
            role=MessageRole.USER,
            content="Hello World",
            artifact=None,
            created_at=datetime.now()
        )

        assert message.get_content_length() == 11  # "Hello World"长度

    def test_create_user_message_factory(self):
        """测试创建用户消息工厂方法"""
        # Act
        message = Message.create_user_message(
            session_id="session-1",
            content="Generate lesson plan"
        )

        # Assert
        assert message.session_id == "session-1"
        assert message.content == "Generate lesson plan"
        assert message.role == MessageRole.USER
        assert message.artifact is None
        assert message.id == "0"

    def test_create_assistant_message_factory(self):
        """测试创建助手消息工厂方法"""
        # Arrange
        artifact = Artifact(
            id="artifact-1",
            type="markdown",
            content="# Lesson Plan",
            created_at=datetime.now()
        )

        # Act
        message = Message.create_assistant_message(
            session_id="session-1",
            content="Here's your lesson plan",
            artifact=artifact
        )

        # Assert
        assert message.session_id == "session-1"
        assert message.content == "Here's your lesson plan"
        assert message.role == MessageRole.ASSISTANT
        assert message.artifact == artifact
        assert message.id == "0"
