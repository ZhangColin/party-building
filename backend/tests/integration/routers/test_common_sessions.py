# -*- coding: utf-8 -*-
"""测试其他路由的关键端点

重点测试：
- common.py: navigation, tasks
- sessions.py: get session, delete session
"""
import pytest


# ==================== common.py 测试 ====================

@pytest.mark.asyncio
async def test_get_navigation(async_client):
    """测试获取导航配置"""
    response = await async_client.get("/api/v1/navigation")

    assert response.status_code == 200
    data = response.json()
    assert "modules" in data


@pytest.mark.asyncio
async def test_get_task_status(logged_in_client):
    """测试获取任务状态（任务不存在）"""
    import uuid
    task_id = str(uuid.uuid4())

    response = await logged_in_client.get(f"/api/v1/tasks/{task_id}")

    # 任务不存在应该返回404或特定状态
    assert response.status_code in [200, 404]


# ==================== 以下测试已废弃（2026-03-02） ====================
# test_common_tools_categories - 端点 /api/v1/common-tools/categories 已删除
# test_common_tools_detail - 端点 /api/v1/common-tools/tools/{id} 已删除
# 原因：前端未使用这些端点，已从 interfaces/routers/common/common.py 中删除
# ==================== sessions.py 测试 ====================

@pytest.mark.asyncio
async def test_get_session_detail_unauthorized(async_client):
    """测试未认证用户获取会话详情"""
    import uuid
    session_id = str(uuid.uuid4())

    response = await async_client.get(f"/api/v1/sessions/{session_id}")

    # 应该返回401未认证
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_session_detail_not_found(logged_in_client):
    """测试获取不存在的会话"""
    import uuid
    session_id = str(uuid.uuid4())

    response = await logged_in_client.get(f"/api/v1/sessions/{session_id}")

    # 应该返回404
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_session_unauthorized(async_client):
    """测试未认证用户删除会话"""
    import uuid
    session_id = str(uuid.uuid4())

    response = await async_client.delete(f"/api/v1/sessions/{session_id}")

    # 应该返回401未认证
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_session_not_found(logged_in_client):
    """测试删除不存在的会话"""
    import uuid
    session_id = str(uuid.uuid4())

    response = await logged_in_client.delete(f"/api/v1/sessions/{session_id}")

    # 应该返回404
    assert response.status_code == 404


# ==================== users.py 测试 ====================

@pytest.mark.asyncio
async def test_get_users_non_admin(logged_in_client):
    """测试非管理员获取用户列表"""
    response = await logged_in_client.get("/api/v1/admin/users")

    # 应该返回403禁止访问
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_non_admin(logged_in_client):
    """测试非管理员创建用户"""
    response = await logged_in_client.post(
        "/api/v1/admin/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_non_admin(logged_in_client):
    """测试非管理员删除用户"""
    import uuid
    user_id = str(uuid.uuid4())

    response = await logged_in_client.delete(f"/api/v1/admin/users/{user_id}")

    assert response.status_code == 403


# ==================== works.py 测试 ====================

@pytest.mark.asyncio
async def test_get_work_categories(logged_in_client):
    """测试获取作品分类"""
    response = await logged_in_client.get("/api/v1/works/categories")

    assert response.status_code == 200
    data = response.json()
    assert "categories" in data


@pytest.mark.asyncio
async def test_get_work_detail_not_found(logged_in_client):
    """测试获取不存在的作品"""
    import uuid
    work_id = str(uuid.uuid4())

    response = await logged_in_client.get(f"/api/v1/works/{work_id}")

    # 应该返回404
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_admin_works_non_admin(logged_in_client):
    """测试非管理员获取作品列表"""
    response = await logged_in_client.get("/api/v1/admin/works")

    assert response.status_code == 403


# ==================== courses.py 测试 ====================

@pytest.mark.asyncio
async def test_get_course_categories(logged_in_client):
    """测试获取课程分类"""
    response = await logged_in_client.get("/api/v1/documents/categories")

    assert response.status_code == 200
    data = response.json()
    assert "categories" in data


@pytest.mark.asyncio
async def test_get_course_documents_by_category(logged_in_client):
    """测试按分类获取课程文档"""
    import uuid
    category_id = str(uuid.uuid4())

    response = await logged_in_client.get(f"/api/v1/documents/category/{category_id}/documents")

    # 分类不存在应该返回空列表或200
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data


@pytest.mark.asyncio
async def test_get_course_document_not_found(logged_in_client):
    """测试获取不存在的课程文档"""
    import uuid
    doc_id = str(uuid.uuid4())

    response = await logged_in_client.get(f"/api/v1/documents/{doc_id}")

    # 应该返回404
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_admin_course_categories_non_admin(logged_in_client):
    """测试非管理员获取课程分类"""
    response = await logged_in_client.get("/api/v1/admin/course-categories")

    assert response.status_code == 403
