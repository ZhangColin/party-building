# -*- coding: utf-8 -*-
"""集成测试配置和fixtures

提供同步TestClient和课程相关的测试fixtures
"""
import pytest
import sys
from pathlib import Path
from typing import Generator

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.database import Base, get_db
from src.main import app
from src.db_models import UserModel, CourseCategoryModel, CourseDocumentModel
from datetime import datetime
import bcrypt


# ==================== 数据库 Fixtures ====================

@pytest.fixture(scope="function")
def integration_db_session() -> Generator[Session, None, None]:
    """
    集成测试数据库会话（同步）
    使用内存SQLite，每个测试函数独立
    """
    # 创建测试引擎
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    # 创建所有表
    Base.metadata.create_all(test_engine)

    # 创建会话
    TestingSessionLocal = sessionmaker(bind=test_engine)
    session = TestingSessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(test_engine)


# ==================== HTTP Client Fixtures ====================

@pytest.fixture(scope="function")
def client(integration_db_session: Session) -> Generator[TestClient, None, None]:
    """
    同步TestClient（用于集成测试）

    覆盖get_db依赖，使用测试数据库会话
    同时替换SessionLocal，确保服务层也能使用测试数据库
    """
    from src.database import SessionLocal
    from src.routers import dependencies

    # 保存原始SessionLocal
    original_session_local = SessionLocal

    # 创建测试用的SessionLocal
    TestingSessionLocal = sessionmaker(bind=integration_db_session.bind)

    # 替换SessionLocal
    import src.database
    import src.services.user_service
    import src.services.auth_service
    import src.services.course_service

    src.database.SessionLocal = TestingSessionLocal
    src.services.user_service.SessionLocal = TestingSessionLocal
    src.services.auth_service.SessionLocal = TestingSessionLocal
    src.services.course_service.SessionLocal = TestingSessionLocal

    # 清除服务缓存，强制重新创建
    dependencies.get_user_service.cache_clear()
    dependencies.get_auth_service.cache_clear()
    dependencies.get_course_service.cache_clear()

    # 覆盖get_db依赖
    def override_get_db():
        try:
            yield integration_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # 清理
    app.dependency_overrides.clear()
    src.database.SessionLocal = original_session_local
    src.services.user_service.SessionLocal = original_session_local
    src.services.auth_service.SessionLocal = original_session_local
    src.services.course_service.SessionLocal = original_session_local
    dependencies.get_user_service.cache_clear()
    dependencies.get_auth_service.cache_clear()
    dependencies.get_course_service.cache_clear()


# ==================== 认证 Fixtures ====================

@pytest.fixture(scope="function")
def test_user(integration_db_session: Session) -> UserModel:
    """创建测试用户（非管理员）"""
    password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = UserModel(
        username="testuser",
        email="test@example.com",
        password_hash=password_hash,
        is_admin=False
    )
    integration_db_session.add(user)
    integration_db_session.commit()
    integration_db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def admin_user(integration_db_session: Session) -> UserModel:
    """创建测试管理员用户"""
    password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = UserModel(
        username="admin",
        email="admin@example.com",
        password_hash=password_hash,
        is_admin=True
    )
    integration_db_session.add(user)
    integration_db_session.commit()
    integration_db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_token(test_user: UserModel) -> str:
    """普通用户认证token"""
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建User实体
    user_entity = User(
        user_id=test_user.user_id,
        username=test_user.username,
        email=test_user.email,
        password_hash=test_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)

    return token


@pytest.fixture(scope="function")
def admin_token(admin_user: UserModel) -> str:
    """管理员认证token"""
    from src.services.auth_service import AuthService
    from src.models import User

    # 创建User实体
    user_entity = User(
        user_id=admin_user.user_id,
        username=admin_user.username,
        email=admin_user.email,
        password_hash=admin_user.password_hash
    )
    auth_service = AuthService()
    token = auth_service.generate_token(user_entity)

    return token


# ==================== 课程相关 Fixtures ====================

@pytest.fixture(scope="function")
def test_category(integration_db_session: Session) -> dict:
    """创建测试课程目录"""
    category = CourseCategoryModel(
        name="测试目录",
        description="这是一个测试目录",
        parent_id=None,
        order=1,
        created_at=datetime.now()
    )
    integration_db_session.add(category)
    integration_db_session.commit()
    integration_db_session.refresh(category)

    return {
        "id": category.category_id,
        "name": category.name,
        "description": category.description
    }


@pytest.fixture(scope="function")
def test_document(integration_db_session: Session, test_category: dict) -> dict:
    """创建测试课程文档"""
    document = CourseDocumentModel(
        title="测试文档",
        summary="这是一个测试文档",
        category_id=test_category["id"],
        content="# 测试文档\n\n这是文档内容",
        order=1,
        created_at=datetime.now()
    )
    integration_db_session.add(document)
    integration_db_session.commit()
    integration_db_session.refresh(document)

    return {
        "id": document.document_id,
        "title": document.title,
        "summary": document.summary,
        "content": document.content
    }
