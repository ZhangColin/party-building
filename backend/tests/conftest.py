# -*- coding: utf-8 -*-
"""pytest统一配置和fixtures"""
import sys
from pathlib import Path

# 添加backend目录到Python路径，确保无论从哪个目录运行都能找到src模块
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# ==================== 测试环境设置 ====================
# 在导入任何模块之前，先创建测试工具配置
# 这样ToolService在初始化时就能找到测试工具

tools_dir = Path("configs/tools/test_tools")
tools_dir.mkdir(parents=True, exist_ok=True)

config_content = """tool_id: text_gen
name: 文本生成
description: AI文本生成工具（测试用）
category: AI工具
visible: true
toolset_id: test_tools
icon: chat-bubble-left
type: normal
order: 1
system_prompt: 你是一个AI助手
welcome_message: |
  欢迎使用文本生成工具
model: deepseek:deepseek-chat
"""

config_file = tools_dir / "text_gen.yaml"
config_file.write_text(config_content, encoding='utf-8')

import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, AsyncGenerator
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

# 重要：在导入src模块之前，先替换掉数据库engine
# 创建测试数据库engine
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)

# 替换掉database.py中的engine和SessionLocal
import src.database
src.database.engine = test_engine
src.database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

from src.database import Base, get_db
from src.main import app
from src.db_models import UserModel


# ==================== 数据库 Fixtures ====================

@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    统一的数据库会话fixture
    - 使用内存SQLite
    - 每个测试函数独立数据库
    - 自动清理
    """
    # 创建所有表
    Base.metadata.create_all(test_engine)

    # 创建会话
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(test_engine)


# ==================== HTTP Client Fixtures ====================

@pytest.fixture(scope="session")
def _app_with_tools():
    """
    创建app实例，确保工具配置已加载

    使用session级别，所有测试共享同一个app实例
    """
    from src.main import app
    from src.routers.dependencies import get_tool_service

    # 清除ToolService缓存，强制重新加载
    get_tool_service.cache_clear()

    # 验证工具可以被找到
    tool_service_1 = get_tool_service()
    tool = tool_service_1.get_tool_by_id("text_gen")

    print(f"\n✓ [Fixture] ToolService实例ID: {id(tool_service_1)}")
    print(f"✓ [Fixture] config_dir: {tool_service_1.config_dir}")
    print(f"✓ [Fixture] 找到工具: {tool}")

    if not tool:
        # 列出所有可用工具
        all_tools = tool_service_1.load_all_tools()
        print(f"✓ [Fixture] 可用工具数量: {len(all_tools)}")
        for t in all_tools:
            print(f"  - {t.tool_id}: {t.name}")

    return app


@pytest.fixture(scope="function")
async def async_client(_app_with_tools, db_session) -> AsyncGenerator[AsyncClient, None]:
    """
    异步HTTP客户端（用于FastAPI集成测试）

    重要：覆盖FastAPI的get_db依赖，使用测试数据库会话
    """
    from src.routers.dependencies import (
        get_user_service,
        get_session_service,
        get_auth_service,
    )
    from src.database import get_db

    # 覆盖数据库依赖，使用测试数据库会话
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    _app_with_tools.dependency_overrides[get_db] = override_get_db

    # 清除所有服务cache，强制重新创建
    get_user_service.cache_clear()
    get_session_service.cache_clear()
    get_auth_service.cache_clear()

    async with AsyncClient(
        transport=ASGITransport(app=_app_with_tools),
        base_url="http://test"
    ) as client:
        yield client

    # 清理
    _app_with_tools.dependency_overrides.clear()
    get_user_service.cache_clear()
    get_session_service.cache_clear()
    get_auth_service.cache_clear()


# ==================== 认证 Fixtures ====================

@pytest.fixture(scope="function")
def test_user(db_session: Session) -> UserModel:
    """创建测试用户（非管理员）"""
    import bcrypt

    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash=password_hash,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    print(f"\n✓ [test_user] 创建用户: {user.username}, user_id={user.user_id}")

    return user


@pytest.fixture(scope="function")
def admin_user(db_session: Session) -> UserModel:
    """创建测试管理员用户"""
    import bcrypt

    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = UserModel(
        username="admin",
        email="admin@example.com",
        password_hash=password_hash,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user: UserModel) -> dict:
    """普通用户认证头"""
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建User实体（AuthService需要User实体，不是UserModel）
    user_entity = User(
        user_id=test_user.user_id,
        username=test_user.username,
        email=test_user.email,
        password_hash=test_user.password_hash  # 添加必填字段
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)

    print(f"\n✓ [auth_headers] token前10字符: {token[:10]}...")
    print(f"✓ [auth_headers] Authorization头: Bearer {token[:20]}...")

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_headers(admin_user: UserModel) -> dict:
    """管理员认证头"""
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建User实体（AuthService需要User实体，不是UserModel）
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash  # 添加必填字段
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)
    return {"Authorization": f"Bearer {token}"}


# ==================== AI Provider Mock Fixtures ====================

@pytest.fixture(scope="function")
def mock_openai_provider():
    """Mock OpenAI Provider（用于单元测试）"""
    from src.infrastructure.providers.openai_provider import OpenAIProvider

    provider = OpenAIProvider(api_key="test-key")

    # Mock客户端
    provider._client = AsyncMock()

    return provider


@pytest.fixture(scope="function")
def mock_deepseek_provider():
    """Mock DeepSeek Provider（用于单元测试）"""
    from src.infrastructure.providers.deepseek_provider import DeepSeekProvider

    provider = DeepSeekProvider(api_key="test-key")

    # Mock客户端
    provider._client = AsyncMock()

    return provider


# ==================== 工具 Fixtures ====================

@pytest.fixture(scope="function")
async def logged_in_client(async_client, db_session):
    """创建已登录的异步客户端（普通用户）"""
    import bcrypt
    from src.db_models import UserModel
    from datetime import datetime

    # 直接在db_session中创建测试用户
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="testuser_logged_in",
        email="test_logged_in@example.com",
        password_hash=password_hash,
        is_admin=False,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 登录获取token
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "testuser_logged_in",
        "password": "password123"
    })

    assert response.status_code == 200, f"Login failed: {response.text}"
    token = response.json()["token"]

    # 设置认证头
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 将用户对象附加到client，方便测试使用
    async_client.test_user = user

    return async_client


@pytest.fixture(scope="function")
async def admin_client(async_client, db_session):
    """创建已登录的管理员客户端"""
    import bcrypt
    from src.db_models import UserModel
    from datetime import datetime

    # 直接在db_session中创建管理员用户
    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = UserModel(
        username="admin_user",
        email="admin@example.com",
        password_hash=password_hash,
        is_admin=True,
        created_at=datetime.now()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 登录获取token
    response = await async_client.post("/api/v1/auth/login", json={
        "account": "admin_user",
        "password": "admin123"
    })

    assert response.status_code == 200, f"Admin login failed: {response.text}"
    token = response.json()["token"]

    # 设置认证头
    async_client.headers["Authorization"] = f"Bearer {token}"

    # 将用户对象附加到client，方便测试使用
    async_client.test_user = user

    return async_client


# test_tool fixture 已删除 - 相关集成测试已移除
