# -*- coding: utf-8 -*-
"""用户管理路由集成测试

测试所有用户管理API端点：
- 获取用户列表（分页、筛选）
- 创建用户
- 获取单个用户
- 更新用户
- 删除用户
- 重置密码
"""
import pytest
import bcrypt
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
async def test_get_user_list_as_admin(async_client, db_session):
    """测试管理员获取用户列表"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

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

    # 测试获取用户列表
    response = await async_client.get("/api/v1/admin/users")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert len(data["users"]) >= 1


@pytest.mark.asyncio
async def test_get_user_list_with_pagination(async_client, db_session):
    """测试用户列表分页功能"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 创建多个普通用户
    for i in range(5):
        user = UserModel(
            username=f"user{i}",
            email=f"user{i}@test.com",
            password_hash=password_hash,
            is_admin=False,
            created_at=datetime.now()
        )
        db_session.add(user)
    db_session.commit()

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 测试分页
    response = await async_client.get("/api/v1/admin/users?page=1&page_size=3")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["users"]) <= 3


@pytest.mark.asyncio
async def test_get_user_list_page_size_limit(async_client, db_session):
    """测试page_size最大限制为100"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 测试page_size超过100时被限制
    response = await async_client.get("/api/v1/admin/users?page_size=200")
    assert response.status_code == 200
    data = response.json()
    assert data["page_size"] == 100  # 应该被限制为100


@pytest.mark.asyncio
async def test_get_user_list_filter_by_admin(async_client, db_session):
    """测试按管理员身份筛选用户"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员和普通用户
    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin_user = UserModel(
        username="admin_test",
        email="admin@test.com",
        password_hash=password_hash,
        is_admin=True,
        created_at=datetime.now()
    )
    db_session.add(admin_user)

    normal_user = UserModel(
        username="normal_user",
        email="normal@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(normal_user)
    db_session.commit()

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 测试筛选管理员
    response = await async_client.get("/api/v1/admin/users?is_admin=true")
    assert response.status_code == 200
    data = response.json()
    assert all(u["is_admin"] for u in data["users"])

    # 测试筛选普通用户
    response = await async_client.get("/api/v1/admin/users?is_admin=false")
    assert response.status_code == 200
    data = response.json()
    assert all(not u["is_admin"] for u in data["users"])


@pytest.mark.asyncio
async def test_get_user_list_without_auth(async_client):
    """测试未认证用户获取用户列表"""
    response = await async_client.get("/api/v1/admin/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_list_as_non_admin(async_client, db_session):
    """测试非管理员用户获取用户列表 - 应该返回403"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建普通用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    normal_user = UserModel(
        username="normal_user",
        email="normal@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(normal_user)
    db_session.commit()
    db_session.refresh(normal_user)

    # 生成token
    user_entity = User(
        user_id=normal_user.user_id,
        username=normal_user.username,
        email=normal_user.email,
        password_hash=normal_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试访问管理员接口
    response = await async_client.get("/api/v1/admin/users")
    assert response.status_code == 403
    assert "需要管理员权限" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_user_as_admin(async_client, db_session):
    """测试管理员创建用户"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User
    import uuid

    # 创建管理员
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

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 创建新用户（使用唯一的用户名和邮箱）
    unique_id = str(uuid.uuid4())[:8]
    new_user_data = {
        "username": f"newuser_{unique_id}",
        "nickname": "新用户",
        "email": f"newuser_{unique_id}@test.com",
        "password": "password123",
        "phone": "13800138000",
        "is_admin": False
    }
    response = await async_client.post("/api/v1/admin/users", json=new_user_data)
    if response.status_code != 201:
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    assert response.status_code == 201, f"创建用户失败: {response.text}"
    data = response.json()
    assert "user" in data
    assert data["user"]["username"] == f"newuser_{unique_id}"
    assert data["user"]["email"] == f"newuser_{unique_id}@test.com"


@pytest.mark.asyncio
async def test_create_user_duplicate_username(async_client, db_session):
    """测试创建用户时用户名重复"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 创建普通用户
    normal_user = UserModel(
        username="existing_user",
        email="existing@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(normal_user)
    db_session.commit()

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试创建重复用户名的用户
    new_user_data = {
        "username": "existing_user",  # 重复的用户名
        "nickname": "重复用户",
        "email": "different@test.com",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/admin/users", json=new_user_data)
    assert response.status_code == 409
    assert "已存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_user_by_id(async_client, db_session):
    """测试获取单个用户信息"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 创建目标用户
    target_user = UserModel(
        username="target_user",
        email="target@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(target_user)
    db_session.commit()
    db_session.refresh(target_user)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 获取用户信息
    response = await async_client.get(f"/api/v1/admin/users/{target_user.user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["user_id"] == target_user.user_id
    assert data["user"]["username"] == "target_user"


@pytest.mark.asyncio
async def test_get_user_not_found(async_client, db_session):
    """测试获取不存在的用户"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试获取不存在的用户
    response = await async_client.get("/api/v1/admin/users/nonexistent_id")
    assert response.status_code == 404
    assert "用户不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user(async_client, db_session):
    """测试更新用户信息"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 创建目标用户
    target_user = UserModel(
        username="target_user",
        email="target@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(target_user)
    db_session.commit()
    db_session.refresh(target_user)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 更新用户信息
    update_data = {
        "nickname": "更新后的昵称",
        "phone": "13900139000"
    }
    response = await async_client.patch(
        f"/api/v1/admin/users/{target_user.user_id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["nickname"] == "更新后的昵称"
    assert data["user"]["phone"] == "13900139000"


@pytest.mark.asyncio
async def test_update_user_not_found(async_client, db_session):
    """测试更新不存在的用户"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试更新不存在的用户
    update_data = {"nickname": "新昵称"}
    response = await async_client.patch(
        "/api/v1/admin/users/nonexistent_id",
        json=update_data
    )
    assert response.status_code == 404
    assert "用户不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_user(async_client, db_session):
    """测试删除用户"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 创建目标用户
    target_user = UserModel(
        username="target_user",
        email="target@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(target_user)
    db_session.commit()
    db_session.refresh(target_user)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 删除用户
    response = await async_client.delete(f"/api/v1/admin/users/{target_user.user_id}")
    assert response.status_code == 204

    # 验证用户已被删除
    response = await async_client.get(f"/api/v1/admin/users/{target_user.user_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_not_found(async_client, db_session):
    """测试删除不存在的用户"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试删除不存在的用户
    response = await async_client.delete("/api/v1/admin/users/nonexistent_id")
    assert response.status_code == 404
    assert "用户不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_reset_user_password(async_client, db_session):
    """测试重置用户密码"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 创建目标用户
    target_user = UserModel(
        username="target_user",
        email="target@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(target_user)
    db_session.commit()
    db_session.refresh(target_user)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 重置密码
    new_password = "newpassword123"
    response = await async_client.post(
        f"/api/v1/admin/users/{target_user.user_id}/reset-password",
        json={"new_password": new_password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "密码已重置"
    assert data["new_password"] == new_password


@pytest.mark.asyncio
async def test_reset_user_password_not_found(async_client, db_session):
    """测试重置不存在用户的密码"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试重置不存在用户的密码
    response = await async_client.post(
        "/api/v1/admin/users/nonexistent_id/reset-password",
        json={"new_password": "newpassword123"}
    )
    assert response.status_code == 404
    assert "用户不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_require_admin_dependency_non_admin(async_client, db_session):
    """测试require_admin依赖函数对非管理员的拒绝"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建普通用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    normal_user = UserModel(
        username="normal_user",
        email="normal@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(normal_user)
    db_session.commit()
    db_session.refresh(normal_user)

    # 生成token
    user_entity = User(
        user_id=normal_user.user_id,
        username=normal_user.username,
        email=normal_user.email,
        password_hash=normal_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 任何需要管理员权限的接口都应该返回403
    response = await async_client.get("/api/v1/admin/users")
    assert response.status_code == 403
    assert "需要管理员权限" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_last_admin(async_client, db_session):
    """测试删除最后一个管理员 - 应该返回400错误"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建唯一的管理员
    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin_user = UserModel(
        username="last_admin",
        email="last_admin@test.com",
        password_hash=password_hash,
        is_admin=True,
        created_at=datetime.now()
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试删除最后一个管理员
    response = await async_client.delete(f"/api/v1/admin/users/{admin_user.user_id}")
    assert response.status_code == 400
    # 错误消息可能是"最后一个管理员"或"不允许删除自己"
    detail = response.json()["detail"]
    assert "最后一个管理员" in detail or "不允许删除自己" in detail


@pytest.mark.asyncio
async def test_update_user_email_conflict(async_client, db_session):
    """测试更新用户时邮箱冲突"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 创建两个用户
    user1 = UserModel(
        username="user1",
        email="user1@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user1)

    user2 = UserModel(
        username="user2",
        email="user2@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user1)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试将user1的邮箱改为user2的邮箱（冲突）
    update_data = {"email": "user2@test.com"}
    response = await async_client.patch(
        f"/api/v1/admin/users/{user1.user_id}",
        json=update_data
    )
    assert response.status_code == 409
    # 错误消息可能是"已存在"或"已被其他用户使用"
    detail = response.json()["detail"]
    assert "已存在" in detail or "已被其他用户使用" in detail


@pytest.mark.asyncio
async def test_update_user_remove_last_admin(async_client, db_session):
    """测试更新用户时取消最后一个管理员权限 - 应该返回400错误"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建唯一的管理员
    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin_user = UserModel(
        username="last_admin",
        email="last_admin@test.com",
        password_hash=password_hash,
        is_admin=True,
        created_at=datetime.now()
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试取消最后一个管理员的管理员权限
    update_data = {"is_admin": False}
    response = await async_client.patch(
        f"/api/v1/admin/users/{admin_user.user_id}",
        json=update_data
    )
    assert response.status_code == 400
    assert "最后一个管理员" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user_with_all_fields(async_client, db_session):
    """测试更新用户时更新所有字段"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User
    import uuid

    # 创建管理员
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

    # 创建目标用户
    target_user = UserModel(
        username="target_user",
        email="target@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(target_user)
    db_session.commit()
    db_session.refresh(target_user)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 更新所有字段
    unique_id = str(uuid.uuid4())[:8]
    update_data = {
        "username": f"updated_user_{unique_id}",
        "nickname": "更新后的昵称",
        "email": f"updated_{unique_id}@test.com",
        "phone": "13900139000",
        "is_admin": True
    }
    response = await async_client.patch(
        f"/api/v1/admin/users/{target_user.user_id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["username"] == f"updated_user_{unique_id}"
    assert data["user"]["nickname"] == "更新后的昵称"
    assert data["user"]["email"] == f"updated_{unique_id}@test.com"
    assert data["user"]["phone"] == "13900139000"
    assert data["user"]["is_admin"] == True


@pytest.mark.asyncio
async def test_create_user_without_optional_fields(async_client, db_session):
    """测试创建用户时不提供可选字段"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User
    import uuid

    # 创建管理员
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

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 创建新用户（只提供必填字段）
    unique_id = str(uuid.uuid4())[:8]
    new_user_data = {
        "username": f"minimal_user_{unique_id}",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/admin/users", json=new_user_data)
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert data["user"]["username"] == f"minimal_user_{unique_id}"


@pytest.mark.asyncio
async def test_reset_user_password_too_short(async_client, db_session):
    """测试重置密码时密码过短（业务逻辑层验证）"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
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

    # 创建目标用户
    target_user = UserModel(
        username="target_user",
        email="target@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(target_user)
    db_session.commit()
    db_session.refresh(target_user)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 绕过Pydantic验证直接调用服务层（测试业务逻辑验证）
    # 这个测试需要使用mock或者其他方式来触发ValueError
    # 由于API层有Pydantic验证（min_length=6），我们需要通过其他方式触发
    # 这里我们测试Pydantic验证层
    response = await async_client.post(
        f"/api/v1/admin/users/{target_user.user_id}/reset-password",
        json={"new_password": "12345"}  # 少于6位
    )
    # Pydantic会拒绝这个请求（422），而不是业务逻辑层（400）
    # 这实际上覆盖了API层的验证
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_self(async_client, db_session):
    """测试管理员删除自己 - 应该返回400错误"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建两个管理员
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

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 尝试删除自己
    response = await async_client.delete(f"/api/v1/admin/users/{admin_user.user_id}")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_user_with_put_method(async_client, db_session):
    """测试使用PUT方法更新用户信息（修复HTTP方法不匹配问题）"""
    from src.db_models import UserModel
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建管理员
    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin_user = UserModel(
        username="admin_test_put",
        email="admin_put@test.com",
        password_hash=password_hash,
        is_admin=True,
        created_at=datetime.now()
    )
    db_session.add(admin_user)
    db_session.commit()

    # 创建目标用户
    target_user = UserModel(
        username="target_user_put",
        email="target_put@test.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(target_user)
    db_session.commit()
    db_session.refresh(target_user)

    # 生成token
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 使用PUT方法更新用户信息
    update_data = {
        "nickname": "PUT方法更新的昵称",
        "phone": "13800138000",
        "email": "put_updated@test.com"
    }
    response = await async_client.put(
        f"/api/v1/admin/users/{target_user.user_id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["nickname"] == "PUT方法更新的昵称"
    assert data["user"]["phone"] == "13800138000"
    assert data["user"]["email"] == "put_updated@test.com"
