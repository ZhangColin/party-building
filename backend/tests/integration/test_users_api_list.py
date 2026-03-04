# -*- coding: utf-8 -*-
"""测试用户列表API

TDD流程：先写失败的测试，再修复代码
"""
import pytest
import bcrypt
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_list_as_admin(async_client, db_session):
    """测试管理员获取用户列表 - 应该返回200而不是500"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User
    from datetime import datetime

    # 创建管理员用户
    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin_user = UserModel(
        username="admin_test",
        email="admin@test.com",
        password_hash=password_hash,
        is_admin=True,
        created_at=datetime.now()
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    # 创建User实体并生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)

    # 设置认证头
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 这个请求应该成功，不应该返回500错误
    response = await async_client.get("/api/v1/admin/users")

    # 断言：应该返回200 OK
    assert response.status_code == 200, f"期望200，实际{response.status_code}，响应: {response.text}"

    # 断言：返回正确的数据结构
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data

    # 应该至少有一个管理员用户
    assert len(data["users"]) >= 1
    assert data["total"] >= 1

    # 额外测试分页参数
    response2 = await async_client.get("/api/v1/admin/users?page=1&page_size=10")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["page"] == 1
    assert data2["page_size"] == 10


@pytest.mark.asyncio
async def test_get_user_list_without_auth(async_client):
    """测试未认证用户获取用户列表"""
    response = await async_client.get("/api/v1/admin/users")
    assert response.status_code == 401
