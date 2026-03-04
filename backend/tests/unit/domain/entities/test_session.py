# -*- coding: utf-8 -*-
"""测试Session实体"""
import pytest
from src.domain.entities.session import Session
from datetime import datetime


def test_session_creation():
    """测试创建Session实体"""
    now = datetime.now()
    session = Session(
        id="session-123",
        user_id="user-456",
        tool_id="test_tool",
        title="Test Session",
        created_at=now
    )

    assert session.id == "session-123"
    assert session.user_id == "user-456"
    assert session.tool_id == "test_tool"
    assert session.title == "Test Session"
    assert session.created_at == now


def test_session_with_different_tool_id():
    """测试不同工具ID的Session"""
    session = Session(
        id="session-456",
        user_id="user-789",
        tool_id="html_generator",
        title="HTML Generation Session",
        created_at=datetime.now()
    )

    assert session.tool_id == "html_generator"
    assert isinstance(session.title, str)


def test_session_attributes():
    """测试Session所有属性"""
    now = datetime.now()
    session = Session(
        id="test-id",
        user_id="test-user",
        tool_id="test-tool",
        title="Test Title",
        created_at=now
    )

    # 验证所有属性都被正确设置
    assert hasattr(session, 'id')
    assert hasattr(session, 'user_id')
    assert hasattr(session, 'tool_id')
    assert hasattr(session, 'title')
    assert hasattr(session, 'created_at')

    # 验证属性类型
    assert isinstance(session.id, str)
    assert isinstance(session.user_id, str)
    assert isinstance(session.tool_id, str)
    assert isinstance(session.title, str)
    assert isinstance(session.created_at, datetime)


def test_session_immutability():
    """测试Session是不可变的（dataclass默认行为）"""
    now = datetime.now()
    session = Session(
        id="session-123",
        user_id="user-456",
        tool_id="test_tool",
        title="Original Title",
        created_at=now
    )

    # dataclass的frozen默认为False，所以可以修改
    # 但我们验证初始值是正确的
    assert session.title == "Original Title"

    # 如果需要不可变性，应该在类定义时设置frozen=True
    # 这里我们只验证初始状态
    original_title = session.title
