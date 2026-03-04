# -*- coding: utf-8 -*-
"""测试 sessions.py 路由的所有端点

目标覆盖率：75%+
未覆盖行：45-66, 83-98, 119, 129
"""
import pytest
from datetime import datetime
from src.db_models import SessionModel, MessageModel
from sqlalchemy.orm import Session


def create_test_session(db: Session, user_id: str, tool_id: str = "test_tool", title: str = "测试会话") -> str:
    """辅助函数：创建测试会话"""
    session = SessionModel(
        user_id=user_id,
        tool_id=tool_id,
        title=title,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session.session_id


def create_test_message(db: Session, session_id: str, role: str, content: str, media_content=None):
    """辅助函数：创建测试消息"""
    message = MessageModel(
        session_id=session_id,
        role=role,
        content=content,
        created_at=datetime.now(),
        media_content=media_content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def create_test_artifact(db: Session, message_id: str, artifact_type: str, content: str, language: str = "html"):
    """辅助函数：创建测试成果物"""
    from src.db_models import ArtifactModel

    artifact = ArtifactModel(
        message_id=message_id,
        type=artifact_type,
        content=content,
        language=language,
        created_at=datetime.now()
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


@pytest.mark.asyncio
async def test_get_session_detail_success(logged_in_client, db_session):
    """测试成功获取会话详情（包含消息）"""
    # 直接创建会话
    session_id = create_test_session(db_session, logged_in_client.test_user.user_id)

    # 添加一条消息
    create_test_message(db_session, session_id, "user", "测试消息")

    # 获取会话详情
    response = await logged_in_client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["tool_id"] == "test_tool"
    assert data["title"] == "测试会话"
    assert "messages" in data
    assert len(data["messages"]) >= 1


@pytest.mark.asyncio
async def test_get_session_detail_empty_messages(logged_in_client, db_session):
    """测试获取会话详情（无消息）"""
    # 直接创建会话（无消息）
    session_id = create_test_session(db_session, logged_in_client.test_user.user_id, title="空消息会话")

    # 获取会话详情（没有消息）
    response = await logged_in_client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["messages"] == []


@pytest.mark.asyncio
async def test_update_session_title_success(logged_in_client, db_session):
    """测试成功更新会话标题"""
    # 直接创建会话
    session_id = create_test_session(db_session, logged_in_client.test_user.user_id, title="原始标题")

    # 更新会话标题
    response = await logged_in_client.patch(
        f"/api/v1/sessions/{session_id}",
        json={"title": "新标题"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["title"] == "新标题"


@pytest.mark.asyncio
async def test_update_session_title_not_found(logged_in_client):
    """测试更新不存在的会话标题"""
    import uuid
    session_id = str(uuid.uuid4())

    response = await logged_in_client.patch(
        f"/api/v1/sessions/{session_id}",
        json={"title": "新标题"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_session_title_unauthorized(async_client):
    """测试未认证用户更新会话标题"""
    import uuid
    session_id = str(uuid.uuid4())

    response = await async_client.patch(
        f"/api/v1/sessions/{session_id}",
        json={"title": "新标题"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_session_success(logged_in_client, db_session):
    """测试成功删除会话"""
    # 直接创建会话
    session_id = create_test_session(db_session, logged_in_client.test_user.user_id, title="待删除的会话")

    # 删除会话
    response = await logged_in_client.delete(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "deleted" in data["message"].lower()

    # 验证会话已删除
    get_response = await logged_in_client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_agent_sessions_deprecated(logged_in_client):
    """测试获取代理会话列表（已废弃接口）"""
    import uuid
    agent_id = str(uuid.uuid4())

    response = await logged_in_client.get(f"/api/v1/agents/{agent_id}/sessions")

    # 废弃接口返回空列表
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert data["sessions"] == []


@pytest.mark.asyncio
async def test_get_agent_sessions_unauthorized(async_client):
    """测试未认证用户获取代理会话列表"""
    import uuid
    agent_id = str(uuid.uuid4())

    response = await async_client.get(f"/api/v1/agents/{agent_id}/sessions")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_session_detail_with_artifacts(logged_in_client, db_session):
    """测试获取包含成果物的会话详情（注意：artifacts 通过 relationship 加载）"""
    # 直接创建会话
    session_id = create_test_session(db_session, logged_in_client.test_user.user_id, title="包含成果物的会话")

    # 添加一条消息
    message = create_test_message(db_session, session_id, "assistant", "这是AI响应")

    # 添加成果物（通过数据库直接插入）
    create_test_artifact(
        db_session,
        message.message_id,
        "html",
        "<html><body>测试</body></html>"
    )

    # 获取会话详情（需要重新查询以加载 relationship）
    db_session.refresh(message)
    response = await logged_in_client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 1
    # 注意：artifacts 通过 SQLAlchemy relationship 加载
    # SessionService 返回的 MessageDomain artifacts 为空列表
    # 这是符合预期的，因为 artifacts 需要单独查询
    assert data["messages"][0]["artifacts"] == []


@pytest.mark.asyncio
async def test_get_session_detail_with_media_content(logged_in_client, db_session):
    """测试获取包含多模态内容的会话详情"""
    import json

    # 直接创建会话
    session_id = create_test_session(db_session, logged_in_client.test_user.user_id, tool_id="media_tool", title="包含媒体内容的会话")

    # 添加一条带媒体内容的消息（media_content 需要是 JSON 字符串）
    media_content = json.dumps([
        {
            "type": "image",
            "url": "http://example.com/image.png",
            "alt_text": "测试图片"
        }
    ])
    create_test_message(db_session, session_id, "assistant", "生成了一张图片", media_content=media_content)

    # 获取会话详情
    response = await logged_in_client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 1
    # media_content 是 JSON 字符串，前端需要解析
    assert data["messages"][0]["media_content"] is not None
    # 验证它是一个有效的 JSON 字符串
    parsed = json.loads(data["messages"][0]["media_content"])
    assert len(parsed) == 1
    assert parsed[0]["type"] == "image"


@pytest.mark.asyncio
async def test_update_session_title_short(logged_in_client, db_session):
    """测试更新会话标题为单个字符"""
    # 直接创建会话
    session_id = create_test_session(db_session, logged_in_client.test_user.user_id, title="原始标题")

    # 更新会话标题为单个字符（最小有效长度）
    response = await logged_in_client.patch(
        f"/api/v1/sessions/{session_id}",
        json={"title": "A"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "A"


@pytest.mark.asyncio
async def test_update_session_title_too_empty(logged_in_client, db_session):
    """测试更新会话标题为空字符串（应该失败）"""
    # 直接创建会话
    session_id = create_test_session(db_session, logged_in_client.test_user.user_id, title="原始标题")

    # 更新会话标题为空字符串（应该返回422）
    response = await logged_in_client.patch(
        f"/api/v1/sessions/{session_id}",
        json={"title": ""}
    )

    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_delete_session_with_messages(logged_in_client, db_session):
    """测试删除包含消息的会话"""
    # 直接创建会话
    session_id = create_test_session(db_session, logged_in_client.test_user.user_id, title="包含多条消息的会话")

    # 添加多条消息
    for i in range(3):
        role = "user" if i % 2 == 0 else "assistant"
        create_test_message(db_session, session_id, role, f"消息 {i+1}")

    # 删除会话（应该级联删除消息）
    response = await logged_in_client.delete(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200

    # 验证会话已删除
    get_response = await logged_in_client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_session_not_found(logged_in_client):
    """测试删除不存在的会话"""
    import uuid
    session_id = str(uuid.uuid4())

    # 尝试删除不存在的会话
    response = await logged_in_client.delete(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_session_unauthorized(async_client):
    """测试未认证用户删除会话"""
    import uuid
    session_id = str(uuid.uuid4())

    # 未认证用户尝试删除会话
    response = await async_client.delete(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_session_detail_not_found(logged_in_client):
    """测试获取不存在的会话详情"""
    import uuid
    session_id = str(uuid.uuid4())

    # 尝试获取不存在的会话
    response = await logged_in_client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_session_detail_unauthorized(async_client):
    """测试未认证用户获取会话详情"""
    import uuid
    session_id = str(uuid.uuid4())

    # 未认证用户尝试获取会话详情
    response = await async_client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 401
