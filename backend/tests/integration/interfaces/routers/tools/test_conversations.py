# -*- coding: utf-8 -*-
"""测试会话管理路由"""
import pytest
from sqlalchemy.orm import Session


@pytest.mark.asyncio
async def test_get_conversations_empty(logged_in_client):
    """测试获取空的会话列表"""
    response = await logged_in_client.get("/api/v1/tools/text_gen/conversations")

    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert isinstance(data["conversations"], list)


@pytest.mark.asyncio
async def test_get_conversations_with_session(
    logged_in_client,
    db_session: Session
):
    """测试获取包含会话的列表"""
    from src.db_models import SessionModel
    from datetime import datetime

    # 使用logged_in_client创建的用户
    user = logged_in_client.test_user

    # 创建测试会话
    session = SessionModel(
        user_id=user.user_id,
        tool_id="text_gen",
        title="测试会话",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    response = await logged_in_client.get("/api/v1/tools/text_gen/conversations")

    assert response.status_code == 200
    data = response.json()
    assert "conversations" in data
    assert len(data["conversations"]) >= 1

    # 验证会话结构
    conv = data["conversations"][0]
    assert "session_id" in conv
    assert "title" in conv
    assert "updated_at" in conv


@pytest.mark.asyncio
async def test_get_conversations_without_auth(async_client):
    """测试未认证用户获取会话列表"""
    response = await async_client.get("/api/v1/tools/text_gen/conversations")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_conversation_success(
    logged_in_client,
    db_session: Session
):
    """测试成功删除会话"""
    from src.db_models import SessionModel
    from datetime import datetime

    # 创建测试会话
    session = SessionModel(
        user_id=logged_in_client.test_user.user_id,
        tool_id="text_gen",
        title="待删除会话",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    response = await logged_in_client.delete(
        f"/api/v1/tools/text_gen/conversations/{session.session_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_delete_conversation_not_found(logged_in_client):
    """测试删除不存在的会话"""
    response = await logged_in_client.delete(
        "/api/v1/tools/text_gen/conversations/nonexistent_session_id"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_conversation_wrong_tool(
    logged_in_client,
    db_session: Session
):
    """测试删除属于不同工具的会话"""
    from src.db_models import SessionModel
    from datetime import datetime

    # 创建属于另一个工具的会话
    session = SessionModel(
        user_id=logged_in_client.test_user.user_id,
        tool_id="other_tool",
        title="其他工具会话",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    response = await logged_in_client.delete(
        f"/api/v1/tools/text_gen/conversations/{session.session_id}"
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_conversation_detail(
    logged_in_client,
    db_session: Session
):
    """测试获取会话详情"""
    from src.db_models import SessionModel, MessageModel
    from datetime import datetime

    # 创建测试会话
    session = SessionModel(
        user_id=logged_in_client.test_user.user_id,
        tool_id="text_gen",
        title="测试会话",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    # 添加测试消息
    message = MessageModel(
        session_id=session.session_id,
        role="user",
        content="测试消息",
        created_at=datetime.now()
    )
    db_session.add(message)
    db_session.commit()

    response = await logged_in_client.get(
        f"/api/v1/tools/text_gen/conversations/{session.session_id}"
    )

    assert response.status_code == 200
    data = response.json()

    # 验证响应结构
    assert "conversation" in data
    assert "messages" in data

    # 验证会话信息
    conv = data["conversation"]
    assert conv["session_id"] == session.session_id
    assert conv["title"] == "测试会话"
    assert conv["tool_id"] == "text_gen"

    # 验证消息列表
    assert len(data["messages"]) >= 1


@pytest.mark.asyncio
async def test_get_conversation_detail_not_found(logged_in_client):
    """测试获取不存在的会话详情"""
    response = await logged_in_client.get(
        "/api/v1/tools/text_gen/conversations/nonexistent_session_id"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_conversation_detail_wrong_tool(
    logged_in_client,
    db_session: Session
):
    """测试获取属于不同工具的会话详情"""
    from src.db_models import SessionModel
    from datetime import datetime

    # 创建属于另一个工具的会话
    session = SessionModel(
        user_id=logged_in_client.test_user.user_id,
        tool_id="other_tool",
        title="其他工具会话",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    response = await logged_in_client.get(
        f"/api/v1/tools/text_gen/conversations/{session.session_id}"
    )

    assert response.status_code == 400
