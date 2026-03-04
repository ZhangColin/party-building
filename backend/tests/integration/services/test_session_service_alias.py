"""
SessionService.get_session_messages 方法测试

测试修复：添加缺失的 get_session_messages 别名方法
"""
import pytest
from src.services.session_service import SessionService
from src.db_models import UserModel, SessionModel, MessageModel
from src.domain.entities.message import Message
from src.domain.value_objects.message_role import MessageRole
from datetime import datetime


def _create_mock_get_db(db_session):
    """
    Create a mock get_db generator function that yields the test's db_session

    This is a helper function to create the mock. It needs to return a generator
    function, not a generator instance, because SessionService stores the function
    and calls it later.
    """
    def mock_get_db():
        """Mock get_db generator that yields the test's db_session"""
        yield db_session
    return mock_get_db


def test_get_session_messages_exists(db_session):
    """测试：get_session_messages方法应该存在（Bug修复验证）"""
    service = SessionService()  # SessionService uses dependency injection, no args needed

    # 验证方法存在
    assert hasattr(service, 'get_session_messages'), \
        "SessionService should have get_session_messages method"


def test_get_session_messages_returns_empty_for_nonexistent_session(db_session):
    """测试：不存在的会话应该返回空列表"""
    service = SessionService()  # SessionService uses dependency injection, no args needed

    # 查询不存在的会话
    messages = service.get_session_messages("nonexistent-session-id")

    assert messages == []


def test_get_session_messages_returns_messages_for_valid_session(db_session):
    """测试：有效的会话应该返回消息列表"""
    # Mock get_db to return the test's db_session
    import src.database

    mock_get_db = _create_mock_get_db(db_session)
    original_get_db = src.database.get_db
    src.database.get_db = mock_get_db

    try:
        service = SessionService()  # Will now use mocked get_db

        # 创建用户
        user = UserModel(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()

        # 创建会话
        session = SessionModel(
            session_id="test-session-123",
            user_id=user.user_id,
            tool_id="test-tool",
            title="Test Session"
        )
        db_session.add(session)
        db_session.commit()

        # 创建消息
        message1 = MessageModel(
            message_id="msg-1",
            session_id="test-session-123",
            role="user",
            content="Hello",
            created_at=datetime.utcnow()
        )
        message2 = MessageModel(
            message_id="msg-2",
            session_id="test-session-123",
            role="assistant",
            content="Hi there",
            created_at=datetime.utcnow()
        )
        db_session.add(message1)
        db_session.add(message2)
        db_session.commit()

        # 获取消息
        messages = service.get_session_messages("test-session-123", user.user_id)

        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"
        assert messages[1].role == "assistant"
        assert messages[1].content == "Hi there"
    finally:
        # Restore original get_db
        src.database.get_db = original_get_db


def test_get_session_messages_validates_user_ownership(db_session):
    """测试：应该验证会话是否属于指定用户"""
    # Mock get_db to return the test's db_session
    import src.database

    mock_get_db = _create_mock_get_db(db_session)
    original_get_db = src.database.get_db
    src.database.get_db = mock_get_db

    try:
        service = SessionService()  # Will now use mocked get_db

        # 创建用户1
        user1 = UserModel(
            username="user1",
            email="user1@example.com",
            password_hash="hashed_password",
            is_admin=False
        )
        db_session.add(user1)

        # 创建用户2
        user2 = UserModel(
            username="user2",
            email="user2@example.com",
            password_hash="hashed_password",
            is_admin=False
        )
        db_session.add(user2)
        db_session.commit()

        # 创建属于user1的会话
        session = SessionModel(
            session_id="user1-session",
            user_id=user1.user_id,
            tool_id="test-tool",
            title="User1 Session"
        )
        db_session.add(session)
        db_session.commit()

        # user2尝试访问user1的会话
        messages = service.get_session_messages("user1-session", user2.user_id)

        # 应该返回空列表（会话不属于user2）
        assert messages == []
    finally:
        # Restore original get_db
        src.database.get_db = original_get_db


def test_get_session_messages_is_alias_of_get_messages_by_session(db_session):
    """测试：get_session_messages应该是get_messages_by_session的别名"""
    # Mock get_db to return the test's db_session
    import src.database

    mock_get_db = _create_mock_get_db(db_session)
    original_get_db = src.database.get_db
    src.database.get_db = mock_get_db

    try:
        service = SessionService()  # Will now use mocked get_db

        # 创建测试会话
        user = UserModel(
            username="aliastest",
            email="alias@example.com",
            password_hash="hashed_password",
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()

        session = SessionModel(
            session_id="alias-session",
            user_id=user.user_id,
            tool_id="test-tool",
            title="Alias Test"
        )
        db_session.add(session)
        db_session.commit()

        # 使用两种方法调用，应该返回相同结果
        result1 = service.get_session_messages("alias-session", user.user_id)
        result2 = service.get_messages_by_session("alias-session", user.user_id)

        assert result1 == result2
    finally:
        # Restore original get_db
        src.database.get_db = original_get_db
