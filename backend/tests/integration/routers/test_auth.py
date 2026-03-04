# -*- coding: utf-8 -*-
"""认证路由集成测试

测试 src/routers/auth.py 的所有端点：
- POST /api/v1/auth/login - 用户登录
- GET /api/v1/auth/me - 获取当前用户信息
- get_current_user 依赖注入函数
"""
import pytest
import bcrypt
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
async def test_login_with_username(async_client, db_session):
    """测试使用用户名登录"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser",
        email="test@example.com",
        phone="13800138000",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 使用用户名登录
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "testuser",
        "password": "password123",
        "remember_me": False
    })

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["username"] == "testuser"
    assert data["expires_in"] == 86400  # 24小时


@pytest.mark.asyncio
async def test_login_with_email(async_client, db_session):
    """测试使用邮箱登录（覆盖行89）"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser2",
        email="test2@example.com",
        phone="13800138001",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 使用邮箱登录
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "test2@example.com",
        "password": "password123",
        "remember_me": False
    })

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "test2@example.com"


@pytest.mark.asyncio
async def test_login_with_phone(async_client, db_session):
    """测试使用手机号登录（覆盖行86）"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser3",
        email="test3@example.com",
        phone="13900139000",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 使用手机号登录
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "13900139000",
        "password": "password123",
        "remember_me": False
    })

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["phone"] == "13900139000"


@pytest.mark.asyncio
async def test_login_with_remember_me(async_client, db_session):
    """测试记住我功能（7天有效期）"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser4",
        email="test4@example.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 登录时设置 remember_me=True
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "testuser4",
        "password": "password123",
        "remember_me": True
    })

    assert response.status_code == 200
    data = response.json()
    assert data["expires_in"] == 604800  # 7天


@pytest.mark.asyncio
async def test_login_with_wrong_password(async_client, db_session):
    """测试密码错误（覆盖行96）"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser5",
        email="test5@example.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 使用错误密码登录
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "testuser5",
        "password": "wrongpassword",
        "remember_me": False
    })

    assert response.status_code == 401
    assert "账号或密码错误" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_with_nonexistent_user(async_client, db_session):
    """测试使用不存在的用户名登录（覆盖行96）"""
    # 使用不存在的用户名登录
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "nonexistent",
        "password": "password123",
        "remember_me": False
    })

    assert response.status_code == 401
    assert "账号或密码错误" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_response_includes_all_user_fields(async_client, db_session):
    """测试登录响应包含所有必要字段"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser6",
        email="test6@example.com",
        nickname="测试用户",
        phone="13800138006",
        password_hash=password_hash,
        is_admin=True,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 登录
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "testuser6",
        "password": "password123",
        "remember_me": False
    })

    assert response.status_code == 200
    data = response.json()
    user_data = data["user"]

    # 验证所有字段都存在
    assert user_data["user_id"] == user.user_id
    assert user_data["username"] == "testuser6"
    assert user_data["email"] == "test6@example.com"
    assert user_data["nickname"] == "测试用户"
    assert user_data["phone"] == "13800138006"
    assert user_data["is_admin"] is True
    # 确保密码不在响应中
    assert "password" not in user_data
    assert "hashed_password" not in user_data


@pytest.mark.asyncio
async def test_get_me_with_valid_token(async_client, db_session):
    """测试使用有效Token获取当前用户信息（覆盖行125）"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser7",
        email="test7@example.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 先登录获取token
    login_response = await async_client.post("/api/v1/auth/login", json={
        "account": "testuser7",
        "password": "password123",
        "remember_me": False
    })
    token = login_response.json()["token"]

    # 使用token获取当前用户信息
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["username"] == "testuser7"
    assert data["user"]["email"] == "test7@example.com"


@pytest.mark.asyncio
async def test_get_me_with_invalid_token(async_client, db_session):
    """测试使用无效Token获取当前用户（覆盖行46）"""
    # 使用伪造的token
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_12345"}
    )

    assert response.status_code == 401
    assert "Token无效或已过期" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_me_without_token(async_client):
    """测试不提供Token获取当前用户"""
    # 不提供Authorization头
    response = await async_client.get("/api/v1/auth/me")

    # FastAPI HTTPBearer在缺少Authorization头时返回401
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_deleted_user(async_client, db_session):
    """测试用户已被删除后的Token（覆盖行56）"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser8",
        email="test8@example.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 先登录获取token
    login_response = await async_client.post("/api/v1/auth/login", json={
        "account": "testuser8",
        "password": "password123",
        "remember_me": False
    })
    token = login_response.json()["token"]

    # 删除用户
    db_session.query(UserModel).filter(
        UserModel.user_id == user.user_id
    ).delete()
    db_session.commit()

    # 使用已删除用户的token
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert "用户不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_with_invalid_phone_format(async_client, db_session):
    """测试使用无效格式的手机号登录"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser9",
        email="test9@example.com",
        phone="13800138009",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 使用无效格式的手机号（少于11位）
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "12345",  # 无效手机号格式
        "password": "password123",
        "remember_me": False
    })

    # 应该当作用户名处理
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_malformed_email(async_client, db_session):
    """测试使用格式错误的邮箱登录"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser10",
        email="test10@example.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 使用格式错误的邮箱
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "invalidemail@",  # 缺少域名部分
        "password": "password123",
        "remember_me": False
    })

    # 应该当作用户名处理
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_empty_account(async_client):
    """测试使用空账号登录"""
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "",
        "password": "password123",
        "remember_me": False
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_with_empty_password(async_client, db_session):
    """测试使用空密码登录"""
    from src.db_models import UserModel

    # 创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser11",
        email="test11@example.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    response = await async_client.post("/api/v1/auth/login", json={
        "account": "testuser11",
        "password": "",
        "remember_me": False
    })

    # 空密码会导致验证错误（422）或登录失败（401）
    # 实际行为是422（FastAPI验证失败）
    assert response.status_code in [401, 422]
