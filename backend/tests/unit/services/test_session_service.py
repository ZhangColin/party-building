# -*- coding: utf-8 -*-
"""SessionService 单元测试"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from src.services.session_service import SessionService
from src.db_models import SessionModel, MessageModel, MessageRole


class TestSessionService:
    """SessionService 测试类"""

    @pytest.fixture
    def service(self):
        """创建 SessionService 实例"""
        return SessionService()

    @pytest.fixture
    def mock_db_session(self):
        """Mock 数据库会话"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_db.query = MagicMock()
        return mock_db

    @pytest.fixture
    def mock_session_model(self):
        """Mock SessionModel"""
        session = MagicMock(spec=SessionModel)
        session.session_id = "test-session-id"
        session.user_id = "test-user-id"
        session.tool_id = "test-tool-id"
        session.title = "测试会话"
        session.created_at = datetime.now()
        session.updated_at = datetime.now()
        return session

    @pytest.fixture
    def mock_message_model(self):
        """Mock MessageModel"""
        message = MagicMock(spec=MessageModel)
        message.message_id = "test-message-id"
        message.session_id = "test-session-id"
        message.role = MessageRole.user
        message.content = "测试消息"
        message.created_at = datetime.now()
        message.media_content = None
        return message

    # ==================== _get_db_session 测试 ====================

    def test_get_db_session_context_manager_normal_flow(self, service):
        """测试数据库会话上下文管理器的正常流程"""
        mock_gen = iter([MagicMock()])
        service._get_db = MagicMock(return_value=mock_gen)

        with service._get_db_session() as db:
            assert db is not None
            db.query("test").first()

        # 验证数据库会话被正确获取
        service._get_db.assert_called_once()

    def test_get_db_session_context_manager_handles_stopiteration(self, service):
        """测试上下文管理器处理 StopIteration 异常（行36-37）"""
        mock_db = MagicMock()
        mock_gen = MagicMock()
        mock_gen.__next__ = Mock(side_effect=[mock_db, StopIteration])

        service._get_db = MagicMock(return_value=mock_gen)

        # 应该正常处理 StopIteration，不抛出异常
        with service._get_db_session() as db:
            assert db is mock_db

    # ==================== create_session 测试 ====================

    @patch('src.services.session_service.SessionService._get_db_session')
    def test_create_session_with_title(self, mock_get_db, service, mock_session_model):
        """测试创建会话（提供标题）"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db
        mock_db.query.return_value.first.return_value = mock_session_model

        result = service.create_session(
            user_id="user123",
            tool_id="tool456",
            title="自定义标题"
        )

        assert result is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('src.services.session_service.SessionService._get_db_session')
    def test_create_session_auto_generate_title_from_first_message(self, mock_get_db, service):
        """测试创建会话时根据第一条消息自动生成标题（行64-74）"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        mock_session = MagicMock(spec=SessionModel)
        mock_session.session_id = "generated-session-id"
        mock_session.user_id = "user123"
        mock_session.tool_id = "tool456"
        mock_session.title = "如何使用Python"
        mock_session.created_at = datetime.now()
        mock_session.updated_at = datetime.now()
        mock_db.refresh.return_value = mock_session

        result = service.create_session(
            user_id="user123",
            tool_id="tool456",
            first_message="如何使用Python进行数据分析？"
        )

        # 验证标题被自动生成（generate_title 最多50字符，不截断）
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        added_session = mock_db.add.call_args[0][0]
        assert added_session.title == "如何使用Python进行数据分析？"

    @patch('src.services.session_service.SessionService._get_db_session')
    def test_create_session_default_title_when_no_first_message(self, mock_get_db, service):
        """测试创建会话时没有第一条消息，使用默认标题（行74）"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        mock_session = MagicMock(spec=SessionModel)
        mock_session.session_id = "session-id"
        mock_session.user_id = "user123"
        mock_session.tool_id = "tool456"
        mock_session.title = "新对话"
        mock_session.created_at = datetime.now()
        mock_session.updated_at = datetime.now()
        mock_db.refresh.return_value = mock_session

        result = service.create_session(
            user_id="user123",
            tool_id="tool456",
            title=None,
            first_message=None
        )

        # 验证使用默认标题"新对话"
        mock_db.add.assert_called_once()
        added_session = mock_db.add.call_args[0][0]
        assert added_session.title == "新对话"

    # ==================== update_session_title 测试 ====================

    @patch('src.services.session_service.SessionService._get_db_session')
    def test_update_session_title_session_not_found(self, mock_get_db, service):
        """测试更新会话标题，会话不存在时返回 None（行161）"""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # 会话不存在
        mock_db.query.return_value = mock_query
        mock_get_db.return_value.__enter__.return_value = mock_db

        result = service.update_session_title(
            session_id="nonexistent-session",
            new_title="新标题",
            user_id="user123"
        )

        # 应该返回 None
        assert result is None
        mock_db.commit.assert_not_called()

    # ==================== add_message 测试 ====================

    @patch('src.services.session_service.SessionService._get_db_session')
    def test_add_message_session_not_found_raises_value_error(self, mock_get_db, service):
        """测试添加消息到不存在的会话，抛出 ValueError（行228）"""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # 会话不存在
        mock_db.query.return_value = mock_query
        mock_get_db.return_value.__enter__.return_value = mock_db

        # 应该抛出 ValueError
        with pytest.raises(ValueError, match="Session '.*' not found"):
            service.add_message(
                session_id="nonexistent-session",
                role="user",
                content="测试消息",
                user_id="user123"
            )

    @patch('src.services.session_service.SessionService._get_db_session')
    def test_add_message_with_custom_created_at(self, mock_get_db, service, mock_session_model):
        """测试添加消息，使用自定义创建时间"""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_session_model
        mock_db.query.return_value = mock_query
        mock_get_db.return_value.__enter__.return_value = mock_db

        custom_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_message = MagicMock(spec=MessageModel)
        mock_message.message_id = "msg-id"
        mock_message.session_id = "test-session-id"
        mock_message.role = MessageRole.user
        mock_message.content = "测试消息"
        mock_message.created_at = custom_time
        mock_db.refresh.return_value = mock_message

        result = service.add_message(
            session_id="test-session-id",
            role="user",
            content="测试消息",
            created_at=custom_time
        )

        # 验证消息使用自定义时间
        added_message = mock_db.add.call_args[0][0]
        assert added_message.created_at == custom_time

    # ==================== create_session_with_id 测试（行343-358）====================

    @pytest.mark.asyncio
    @patch('src.services.session_service.SessionService._get_db_session')
    async def test_create_session_with_id_success(self, mock_get_db, service):
        """测试使用指定ID创建会话（异步方法，行343-358）"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        mock_session = MagicMock(spec=SessionModel)
        mock_session.session_id = "custom-session-id"
        mock_session.user_id = "user123"
        mock_session.tool_id = "tool456"
        mock_session.title = "自定义会话"
        mock_session.created_at = datetime.now()
        mock_session.updated_at = datetime.now()
        mock_db.refresh.return_value = mock_session

        result = await service.create_session_with_id(
            session_id="custom-session-id",
            user_id="user123",
            tool_id="tool456",
            title="自定义会话"
        )

        # 验证会话被创建
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        added_session = mock_db.add.call_args[0][0]
        assert added_session.session_id == "custom-session-id"
        assert added_session.title == "自定义会话"

    # ==================== save_message 测试（行391-413）====================

    @pytest.mark.asyncio
    @patch('src.services.session_service.SessionService._get_db_session')
    async def test_save_message_success(self, mock_get_db, service):
        """测试保存消息（异步方法，行391-413）"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock 消息
        mock_message = MagicMock(spec=MessageModel)
        mock_message.message_id = "msg-id"
        mock_message.session_id = "session-id"
        mock_message.role = MessageRole.assistant
        mock_message.content = "AI回复"
        mock_message.created_at = datetime.now()
        mock_db.refresh.return_value = mock_message

        # Mock 会话查询（用于更新 updated_at）
        mock_session = MagicMock(spec=SessionModel)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_session
        mock_db.query.return_value = mock_query

        result = await service.save_message(
            message_id="msg-id",
            session_id="session-id",
            role="assistant",
            content="AI回复"
        )

        # 验证消息被保存
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

        # 验证会话的 updated_at 被更新
        assert mock_session.updated_at is not None

    @pytest.mark.asyncio
    @patch('src.services.session_service.SessionService._get_db_session')
    async def test_save_message_session_not_found(self, mock_get_db, service):
        """测试保存消息时会话不存在（行409-412逻辑）"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock 消息
        mock_message = MagicMock(spec=MessageModel)
        mock_message.message_id = "msg-id"
        mock_db.refresh.return_value = mock_message

        # Mock 会话查询返回 None（会话不存在）
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # 即使会话不存在，也应该能保存消息（不更新会话）
        result = await service.save_message(
            message_id="msg-id",
            session_id="nonexistent-session",
            role="assistant",
            content="AI回复"
        )

        # 验证消息被保存
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

    # ==================== save_message_with_media 测试（行436-461）====================

    @pytest.mark.asyncio
    @patch('src.services.session_service.SessionService._get_db_session')
    async def test_save_message_with_media_success(self, mock_get_db, service):
        """测试保存多模态消息（异步方法，行436-461）"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock 消息
        mock_message = MagicMock(spec=MessageModel)
        mock_message.message_id = "msg-id"
        mock_message.session_id = "session-id"
        mock_message.role = MessageRole.user
        mock_message.content = "查看这张图片"
        mock_message.created_at = datetime.now()
        mock_db.refresh.return_value = mock_message

        # Mock 会话查询
        mock_session = MagicMock(spec=SessionModel)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_session
        mock_db.query.return_value = mock_query

        media_json = '{"type": "image", "url": "http://example.com/image.jpg"}'

        result = await service.save_message_with_media(
            message_id="msg-id",
            session_id="session-id",
            role="user",
            content="查看这张图片",
            media_content=media_json
        )

        # 验证消息被保存
        mock_db.add.assert_called_once()
        added_message = mock_db.add.call_args[0][0]
        assert added_message.media_content == media_json
        mock_db.commit.assert_called()

        # 验证会话的 updated_at 被更新
        assert mock_session.updated_at is not None

    @pytest.mark.asyncio
    @patch('src.services.session_service.SessionService._get_db_session')
    async def test_save_message_with_media_empty_content(self, mock_get_db, service):
        """测试保存多模态消息，内容为空"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock 消息
        mock_message = MagicMock(spec=MessageModel)
        mock_message.message_id = "msg-id"
        mock_db.refresh.return_value = mock_message

        # Mock 会话查询
        mock_session = MagicMock(spec=SessionModel)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_session
        mock_db.query.return_value = mock_query

        media_json = '{"type": "image", "url": "http://example.com/image.jpg"}'

        result = await service.save_message_with_media(
            message_id="msg-id",
            session_id="session-id",
            role="user",
            content="",  # 空内容
            media_content=media_json
        )

        # 验证消息被保存
        mock_db.add.assert_called_once()
        added_message = mock_db.add.call_args[0][0]
        assert added_message.content == ""
        assert added_message.media_content == media_json

    @pytest.mark.asyncio
    @patch('src.services.session_service.SessionService._get_db_session')
    async def test_save_message_with_media_session_not_found(self, mock_get_db, service):
        """测试保存多模态消息时会话不存在"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Mock 消息
        mock_message = MagicMock(spec=MessageModel)
        mock_message.message_id = "msg-id"
        mock_db.refresh.return_value = mock_message

        # Mock 会话查询返回 None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        media_json = '{"type": "image", "url": "http://example.com/image.jpg"}'

        # 即使会话不存在，也应该能保存消息
        result = await service.save_message_with_media(
            message_id="msg-id",
            session_id="nonexistent-session",
            role="user",
            content="查看图片",
            media_content=media_json
        )

        # 验证消息被保存
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()

    # ==================== get_session 测试 ====================

    @pytest.mark.asyncio
    @patch('src.services.session_service.SessionService.get_session_by_id')
    async def test_get_session_async_wrapper(self, mock_get_by_id, service):
        """测试 get_session 异步包装方法"""
        mock_session = MagicMock()
        mock_session.session_id = "session-id"
        mock_get_by_id.return_value = mock_session

        result = await service.get_session("session-id")

        mock_get_by_id.assert_called_once_with("session-id")
        assert result is not None
