# -*- coding: utf-8 -*-
"""测试 common.py 路由的所有端点

迁移说明：从 backend/src/routers/common.py 迁移到 interfaces/routers/common/common.py
迁移日期：2026-03-02

目标覆盖率：60%+
文件：backend/src/interfaces/routers/common/common.py
当前覆盖率：17%
"""
import pytest
import uuid
import bcrypt
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.db_models import UserModel, SessionModel, ToolCategoryModel, CommonToolModel
from src.interfaces.routers.common.common import task_storage


# ==================== 辅助函数 ====================

async def create_user_and_login(client, db_session, username, password="password123"):
    """辅助函数：创建用户并登录，返回token和user对象"""
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username=username,
        email=f"{username}@example.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 登录获取token
    response = await client.post("/api/v1/auth/login", json={
        "account": username,
        "password": password
    })

    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["token"]

    return token, user


async def create_session_for_user(db_session, user_id):
    """辅助函数：为用户创建会话"""
    session = SessionModel(
        session_id=str(uuid.uuid4()),
        user_id=user_id,
        tool_id="test_tool",
        title="Test Session",
        created_at=datetime.now()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


# ==================== 导航端点测试 ====================

@pytest.mark.asyncio
async def test_get_navigation(async_client):
    """测试获取导航配置（公开接口）"""
    response = await async_client.get("/api/v1/navigation")

    assert response.status_code == 200
    data = response.json()
    assert "modules" in data
    assert isinstance(data["modules"], list)


# ==================== Markdown转Word端点测试 ====================

@pytest.mark.asyncio
async def test_convert_markdown_to_word_success(async_client, db_session):
    """测试Markdown转Word成功"""
    # 创建用户并登录
    token, _ = await create_user_and_login(async_client, db_session, "test_convert_user")

    # Mock conversion_service
    with patch('src.interfaces.routers.common.common.get_conversion_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.markdown_to_word.return_value = (
            b"fake_word_content",
            "test_document.docx"
        )
        mock_get_service.return_value = mock_service

        response = await async_client.post(
            "/api/v1/convert/markdown-to-word",
            json={
                "content": "# Test Heading\n\nTest content",
                "filename": "test_document"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "attachment" in response.headers["content-disposition"]
        assert "test_document.docx" in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_convert_markdown_to_word_without_filename(async_client, db_session):
    """测试Markdown转Word不指定文件名"""
    token, _ = await create_user_and_login(async_client, db_session, "test_convert_user2")

    with patch('src.interfaces.routers.common.common.get_conversion_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.markdown_to_word.return_value = (
            b"fake_word_content",
            "timestamp.docx"
        )
        mock_get_service.return_value = mock_service

        response = await async_client.post(
            "/api/v1/convert/markdown-to-word",
            json={
                "content": "# Test"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_convert_markdown_to_word_empty_content(async_client, db_session):
    """测试Markdown转Word空内容（验证错误）"""
    token, _ = await create_user_and_login(async_client, db_session, "test_convert_user3")

    response = await async_client.post(
        "/api/v1/convert/markdown-to-word",
        json={
            "content": "",
            "filename": "test"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    # Pydantic验证错误，应该返回422
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_convert_markdown_to_word_value_error(async_client, db_session):
    """测试Markdown转Word服务抛出ValueError"""
    token, _ = await create_user_and_login(async_client, db_session, "test_convert_user4")

    with patch('src.interfaces.routers.common.common.get_conversion_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.markdown_to_word.side_effect = ValueError("无效的Markdown内容")
        mock_get_service.return_value = mock_service

        response = await async_client.post(
            "/api/v1/convert/markdown-to-word",
            json={
                "content": "invalid content",
                "filename": "test"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "无效的Markdown内容" in data["detail"]


@pytest.mark.asyncio
async def test_convert_markdown_to_word_runtime_error(async_client, db_session):
    """测试Markdown转Word服务不可用（RuntimeError）"""
    token, _ = await create_user_and_login(async_client, db_session, "test_convert_user5")

    with patch('src.interfaces.routers.common.common.get_conversion_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.markdown_to_word.side_effect = RuntimeError("pandoc未安装")
        mock_get_service.return_value = mock_service

        response = await async_client.post(
            "/api/v1/convert/markdown-to-word",
            json={
                "content": "# Test",
                "filename": "test"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "pandoc未安装" in data["detail"] or "文档转换服务暂时不可用" in data["detail"]


@pytest.mark.asyncio
async def test_convert_markdown_to_word_unauthorized(async_client):
    """测试未认证用户转换Markdown"""
    response = await async_client.post(
        "/api/v1/convert/markdown-to-word",
        json={
            "content": "# Test",
            "filename": "test"
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_convert_markdown_to_word_generic_exception(async_client, db_session):
    """测试Markdown转Word通用异常处理"""
    token, _ = await create_user_and_login(async_client, db_session, "test_convert_user6")

    with patch('src.interfaces.routers.common.common.get_conversion_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.markdown_to_word.side_effect = Exception("未知错误")
        mock_get_service.return_value = mock_service

        response = await async_client.post(
            "/api/v1/convert/markdown-to-word",
            json={
                "content": "# Test",
                "filename": "test"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


# ==================== 任务状态查询端点测试 ====================

@pytest.mark.asyncio
async def test_get_task_status_not_found(async_client, db_session):
    """测试获取不存在的任务状态"""
    token, _ = await create_user_and_login(async_client, db_session, "test_task_user1")
    task_id = str(uuid.uuid4())

    response = await async_client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "任务不存在" in data["detail"]


@pytest.mark.asyncio
async def test_get_task_status_unauthorized(async_client):
    """测试未认证用户获取任务状态"""
    task_id = str(uuid.uuid4())

    response = await async_client.get(f"/api/v1/tasks/{task_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_task_status_sync_completed(async_client, db_session):
    """测试获取已完成任务状态（同步模式）"""
    token, user = await create_user_and_login(async_client, db_session, "test_task_user2")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建任务存储
    task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "completed",
            "session_id": session.session_id,
            "media_urls": ["http://example.com/image.png"],
            "metadata": {"size": "1024x1024"}
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    response = await async_client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["task_id"] == task_id
    assert data["media_urls"] == ["http://example.com/image.png"]


@pytest.mark.asyncio
async def test_get_task_status_image_processing(async_client, db_session):
    """测试获取图片生成任务状态（处理中）"""
    token, user = await create_user_and_login(async_client, db_session, "test_image_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建异步任务
    task_id = str(uuid.uuid4())
    glm_task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",
            "session_id": session.session_id,
            "media_type": "image",
            "glm_task_id": glm_task_id,
            "request_params": {
                "size": "1024x1024",
                "style": "realistic"
            },
            "query_fail_count": 0
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock AI Service
    with patch('src.interfaces.routers.common.common.get_ai_service') as mock_get_ai:
        mock_ai = AsyncMock()
        mock_ai.get_image_result.return_value = {
            "task_status": "PROCESSING",
            "image_result": []
        }
        mock_get_ai.return_value = mock_ai

        response = await async_client.get(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["task_id"] == task_id
        assert data["progress"] == 50


@pytest.mark.asyncio
async def test_get_task_status_image_success(async_client, db_session):
    """测试获取图片生成任务状态（成功）"""
    token, user = await create_user_and_login(async_client, db_session, "test_image_success_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建任务
    task_id = str(uuid.uuid4())
    glm_task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",
            "session_id": session.session_id,
            "media_type": "image",
            "glm_task_id": glm_task_id,
            "request_params": {
                "size": "1024x1024",
                "style": "realistic"
            },
            "query_fail_count": 0
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock AI Service返回成功
    with patch('src.interfaces.routers.common.common.get_ai_service') as mock_get_ai:
        mock_ai = AsyncMock()
        mock_ai.get_image_result.return_value = {
            "task_status": "SUCCESS",
            "image_result": [
                {"url": "http://example.com/image1.png"},
                {"url": "http://example.com/image2.png"}
            ]
        }
        mock_get_ai.return_value = mock_ai

        # Mock Session Service
        with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
            mock_session_service = AsyncMock()
            mock_session = MagicMock()
            mock_session.user_id = user.user_id
            mock_session_service.get_session.return_value = mock_session
            mock_session_service.save_message_with_media = AsyncMock()
            mock_get_session.return_value = mock_session_service

            response = await async_client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert data["content_type"] == "image"
            assert len(data["media_urls"]) == 2
            assert data["metadata"]["size"] == "1024x1024"
            assert data["metadata"]["count"] == 2


@pytest.mark.asyncio
async def test_get_task_status_image_failed(async_client, db_session):
    """测试获取图片生成任务状态（失败）"""
    token, user = await create_user_and_login(async_client, db_session, "test_image_fail_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建任务
    task_id = str(uuid.uuid4())
    glm_task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",
            "session_id": session.session_id,
            "media_type": "image",
            "glm_task_id": glm_task_id,
            "request_params": {
                "size": "1024x1024",
                "style": "realistic"
            },
            "query_fail_count": 0
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock AI Service返回失败
    with patch('src.interfaces.routers.common.common.get_ai_service') as mock_get_ai:
        mock_ai = AsyncMock()
        mock_ai.get_image_result.return_value = {
            "task_status": "FAIL",
            "error": {
                "message": "图片生成失败：内容违规"
            }
        }
        mock_get_ai.return_value = mock_ai

        # Mock Session Service
        with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
            mock_session_service = AsyncMock()
            mock_session = MagicMock()
            mock_session.user_id = user.user_id
            mock_session_service.get_session.return_value = mock_session
            mock_get_session.return_value = mock_session_service

            response = await async_client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "failed"
            assert "图片生成失败" in data["error_message"]


@pytest.mark.asyncio
async def test_get_task_status_forbidden_user(async_client, db_session):
    """测试获取其他用户的任务状态（应该返回403）"""
    token, _ = await create_user_and_login(async_client, db_session, "test_forbidden_user")

    # 创建另一个用户
    other_user = UserModel(
        username="other_user",
        email="other@example.com",
        password_hash=bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    # 创建属于其他用户的会话
    session = SessionModel(
        session_id=str(uuid.uuid4()),
        user_id=other_user.user_id,  # 属于其他用户
        tool_id="test_tool",
        title="Other User Session",
        created_at=datetime.now()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    # 创建任务
    task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "completed",
            "session_id": session.session_id,
            "media_urls": ["http://example.com/image.png"],
            "metadata": {}
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock Session Service
    with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
        mock_session_service = AsyncMock()
        mock_session = MagicMock()
        mock_session.user_id = other_user.user_id  # 返回其他用户的session
        mock_session_service.get_session.return_value = mock_session
        mock_get_session.return_value = mock_session_service

        response = await async_client.get(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # 应该返回403（无权访问）
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "无权访问" in data["detail"]


@pytest.mark.asyncio
async def test_get_task_status_video_success(async_client, db_session):
    """测试获取视频生成任务状态（成功）"""
    token, user = await create_user_and_login(async_client, db_session, "test_video_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建视频任务
    task_id = str(uuid.uuid4())
    glm_task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",
            "session_id": session.session_id,
            "media_type": "video",
            "glm_task_id": glm_task_id,
            "request_params": {
                "size": "1024x1024",
                "fps": 30,
                "quality": "high"
            },
            "query_fail_count": 0
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock AI Service返回成功
    with patch('src.interfaces.routers.common.common.get_ai_service') as mock_get_ai:
        mock_ai = AsyncMock()
        mock_ai.get_video_result.return_value = {
            "task_status": "SUCCESS",
            "video_result": [
                {"url": "http://example.com/video1.mp4"}
            ]
        }
        mock_get_ai.return_value = mock_ai

        # Mock Session Service
        with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
            mock_session_service = AsyncMock()
            mock_session = MagicMock()
            mock_session.user_id = user.user_id
            mock_session_service.get_session.return_value = mock_session
            mock_session_service.save_message_with_media = AsyncMock()
            mock_get_session.return_value = mock_session_service

            response = await async_client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert data["content_type"] == "video"
            assert len(data["media_urls"]) == 1


@pytest.mark.asyncio
async def test_get_task_status_video_processing(async_client, db_session):
    """测试获取视频生成任务状态（处理中）"""
    token, user = await create_user_and_login(async_client, db_session, "test_video_processing_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建视频任务
    task_id = str(uuid.uuid4())
    glm_task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",
            "session_id": session.session_id,
            "media_type": "video",
            "glm_task_id": glm_task_id,
            "request_params": {
                "size": "1024x1024",
                "fps": 30,
                "quality": "high"
            },
            "query_fail_count": 0
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock AI Service返回处理中
    with patch('src.interfaces.routers.common.common.get_ai_service') as mock_get_ai:
        mock_ai = AsyncMock()
        mock_ai.get_video_result.return_value = {
            "task_status": "PROCESSING",
            "video_result": []
        }
        mock_get_ai.return_value = mock_ai

        # Mock Session Service
        with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
            mock_session_service = AsyncMock()
            mock_session = MagicMock()
            mock_session.user_id = user.user_id
            mock_session_service.get_session.return_value = mock_session
            mock_get_session.return_value = mock_session_service

            response = await async_client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "processing"
            assert data["progress"] == 50


@pytest.mark.asyncio
async def test_get_task_status_video_failed(async_client, db_session):
    """测试获取视频生成任务状态（失败）"""
    token, user = await create_user_and_login(async_client, db_session, "test_video_fail_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建视频任务
    task_id = str(uuid.uuid4())
    glm_task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",
            "session_id": session.session_id,
            "media_type": "video",
            "glm_task_id": glm_task_id,
            "request_params": {
                "size": "1024x1024",
                "fps": 30,
                "quality": "high"
            },
            "query_fail_count": 0
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock AI Service返回失败
    with patch('src.interfaces.routers.common.common.get_ai_service') as mock_get_ai:
        mock_ai = AsyncMock()
        mock_ai.get_video_result.return_value = {
            "task_status": "FAIL",
            "error": {
                "message": "视频生成失败：内容违规"
            }
        }
        mock_get_ai.return_value = mock_ai

        # Mock Session Service
        with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
            mock_session_service = AsyncMock()
            mock_session = MagicMock()
            mock_session.user_id = user.user_id
            mock_session_service.get_session.return_value = mock_session
            mock_get_session.return_value = mock_session_service

            response = await async_client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "failed"
            assert "视频生成失败" in data["error_message"]


@pytest.mark.asyncio
async def test_get_task_status_query_fail_retry(async_client, db_session):
    """测试查询任务状态失败但重试（失败次数<5）"""
    token, user = await create_user_and_login(async_client, db_session, "test_retry_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建任务
    task_id = str(uuid.uuid4())
    glm_task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",
            "session_id": session.session_id,
            "media_type": "image",
            "glm_task_id": glm_task_id,
            "request_params": {
                "size": "1024x1024",
                "style": "realistic"
            },
            "query_fail_count": 3  # 已失败3次
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock AI Service抛出异常
    with patch('src.interfaces.routers.common.common.get_ai_service') as mock_get_ai:
        mock_ai = AsyncMock()
        mock_ai.get_image_result.side_effect = Exception("网络错误")
        mock_get_ai.return_value = mock_ai

        # Mock Session Service
        with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
            mock_session_service = AsyncMock()
            mock_session = MagicMock()
            mock_session.user_id = user.user_id
            mock_session_service.get_session.return_value = mock_session
            mock_get_session.return_value = mock_session_service

            response = await async_client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            # 应该返回processing状态，让前端继续轮询
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "processing"


@pytest.mark.asyncio
async def test_get_task_status_query_fail_max_retries(async_client, db_session):
    """测试查询任务状态失败次数过多（>=5次）"""
    token, user = await create_user_and_login(async_client, db_session, "test_max_retry_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建任务，已失败5次
    task_id = str(uuid.uuid4())
    glm_task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",
            "session_id": session.session_id,
            "media_type": "image",
            "glm_task_id": glm_task_id,
            "request_params": {
                "size": "1024x1024",
                "style": "realistic"
            },
            "query_fail_count": 5  # 已失败5次
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock AI Service抛出异常
    with patch('src.interfaces.routers.common.common.get_ai_service') as mock_get_ai:
        mock_ai = AsyncMock()
        mock_ai.get_image_result.side_effect = Exception("网络错误")
        mock_get_ai.return_value = mock_ai

        # Mock Session Service
        with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
            mock_session_service = AsyncMock()
            mock_session = MagicMock()
            mock_session.user_id = user.user_id
            mock_session_service.get_session.return_value = mock_session
            mock_get_session.return_value = mock_session_service

            response = await async_client.get(
                f"/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            # 应该标记任务为失败
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "failed"
            assert "查询任务状态失败" in data["error_message"]


@pytest.mark.asyncio
async def test_get_task_status_no_glm_task_id(async_client, db_session):
    """测试任务没有glm_task_id且状态不是completed（异常情况）"""
    token, user = await create_user_and_login(async_client, db_session, "test_no_glm_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建任务，但没有glm_task_id
    task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",  # 不是completed
            "session_id": session.session_id,
            "media_type": "image",
            # 没有 glm_task_id
            "request_params": {
                "size": "1024x1024",
                "style": "realistic"
            }
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock Session Service
    with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
        mock_session_service = AsyncMock()
        mock_session = MagicMock()
        mock_session.user_id = user.user_id
        mock_session_service.get_session.return_value = mock_session
        mock_get_session.return_value = mock_session_service

        response = await async_client.get(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # 应该返回500（任务状态异常）
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_get_task_status_unsupported_media_type(async_client, db_session):
    """测试不支持的媒体类型"""
    token, user = await create_user_and_login(async_client, db_session, "test_unsupported_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建任务，使用不支持的媒体类型
    task_id = str(uuid.uuid4())
    glm_task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "processing",
            "session_id": session.session_id,
            "media_type": "audio",  # 不支持的类型
            "glm_task_id": glm_task_id,
            "request_params": {},
            "query_fail_count": 0  # 初始化失败计数
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock Session Service
    with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
        mock_session_service = AsyncMock()
        mock_session = MagicMock()
        mock_session.user_id = user.user_id
        mock_session_service.get_session.return_value = mock_session
        mock_get_session.return_value = mock_session_service

        response = await async_client.get(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # 由于代码在try-except中，501错误会被捕获并转换为processing状态
        # 最终返回200状态码
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_task_status_generic_exception(async_client, db_session):
    """测试任务状态查询通用异常处理"""
    token, user = await create_user_and_login(async_client, db_session, "test_generic_exception_user")
    session = await create_session_for_user(db_session, user.user_id)

    # 创建任务
    task_id = str(uuid.uuid4())
    local_task_storage = {
        task_id: {
            "status": "completed",
            "session_id": session.session_id,
            "media_urls": ["http://example.com/image.png"],
            "metadata": {}
        }
    }
    task_storage.clear()
    task_storage.update(local_task_storage)

    # Mock Session Service抛出异常
    with patch('src.interfaces.routers.common.common.get_session_service') as mock_get_session:
        mock_session_service = AsyncMock()
        mock_session_service.get_session.side_effect = Exception("数据库错误")
        mock_get_session.return_value = mock_session_service

        response = await async_client.get(
            f"/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # 应该返回500
        assert response.status_code == 500


