# -*- coding: utf-8 -*-
"""UserService 单元测试"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from src.services.user_service import UserService
from src.models import User
from src.db_models import UserModel


class TestUserService:
    """UserService 测试类"""

    def test_init(self):
        """测试初始化"""
        service = UserService()
        assert service is not None

    # ==================== create_user 测试 ====================

    @patch('src.services.user_service.SessionLocal')
    def test_create_user_success(self, mock_session_local):
        """测试成功创建用户"""
        # Mock 数据库会话
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.create_user(
            username="testuser",
            password="password123",
            nickname="测试用户",
            email="test@example.com",
            phone="13800138000"
        )

        assert result is not None
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert result.phone == "13800138000"
        assert result.nickname == "测试用户"
        assert result.password_hash is not None
        assert len(result.password_hash) > 0
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch('src.services.user_service.SessionLocal')
    def test_create_user_with_minimal_fields(self, mock_session_local):
        """测试使用最少字段创建用户"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.create_user(
            username="minuser",
            password="pass123"
        )

        assert result.username == "minuser"
        assert result.nickname is None
        assert result.email is None
        assert result.phone is None
        assert result.is_admin is False

    @patch('src.services.user_service.SessionLocal')
    def test_create_user_as_admin(self, mock_session_local):
        """测试创建管理员用户"""
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.create_user(
            username="admin",
            password="admin123",
            is_admin=True
        )

        assert result.is_admin is True

    @patch('src.services.user_service.SessionLocal')
    def test_create_user_duplicate_username(self, mock_session_local):
        """测试创建用户时用户名重复"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
        mock_db.commit.side_effect = IntegrityError("Duplicate", {}, None)
        mock_session_local.return_value = mock_db

        service = UserService()

        with pytest.raises(ValueError, match="用户名已存在"):
            service.create_user(
                username="existing",
                password="password123"
            )

        mock_db.rollback.assert_called_once()

    @patch('src.services.user_service.SessionLocal')
    def test_create_user_duplicate_email(self, mock_session_local):
        """测试创建用户时邮箱重复"""
        mock_db = MagicMock()
        # 第一个查询返回None（用户名不存在）
        # 第二个查询返回对象（邮箱已存在）
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = [None, MagicMock()]
        mock_db.query.return_value = mock_query
        mock_db.commit.side_effect = IntegrityError("Duplicate", {}, None)
        mock_session_local.return_value = mock_db

        service = UserService()

        with pytest.raises(ValueError, match="邮箱已存在"):
            service.create_user(
                username="newuser",
                password="password123",
                email="existing@example.com"
            )

    @patch('src.services.user_service.SessionLocal')
    def test_create_user_unknown_integrity_error(self, mock_session_local):
        """测试创建用户时未知的数据完整性错误"""
        mock_db = MagicMock()
        mock_query = MagicMock()
        # 所有查询都返回None
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        mock_db.commit.side_effect = IntegrityError("Unknown", {}, None)
        mock_session_local.return_value = mock_db

        service = UserService()

        with pytest.raises(ValueError, match="创建用户失败"):
            service.create_user(
                username="newuser",
                password="password123"
            )

    # ==================== get_user_by_email 测试 ====================

    @patch('src.services.user_service.SessionLocal')
    def test_get_user_by_email_found(self, mock_session_local):
        """测试根据邮箱查找用户 - 找到"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="testuser",
            nickname="测试",
            email="test@example.com",
            phone="13800138000",
            password_hash="hash123",
            avatar="avatar.jpg",
            is_admin=False,
            created_at=datetime.now()
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.get_user_by_email("test@example.com")

        assert result is not None
        assert result.email == "test@example.com"
        assert result.username == "testuser"

    @patch('src.services.user_service.SessionLocal')
    def test_get_user_by_email_not_found(self, mock_session_local):
        """测试根据邮箱查找用户 - 未找到"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.get_user_by_email("nonexistent@example.com")

        assert result is None

    # ==================== get_user_by_phone 测试 ====================

    @patch('src.services.user_service.SessionLocal')
    def test_get_user_by_phone_found(self, mock_session_local):
        """测试根据手机号查找用户 - 找到"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="testuser",
            nickname="测试",
            email="test@example.com",
            phone="13800138000",
            password_hash="hash123",
            avatar="avatar.jpg",
            is_admin=False,
            created_at=datetime.now()
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.get_user_by_phone("13800138000")

        assert result is not None
        assert result.phone == "13800138000"

    @patch('src.services.user_service.SessionLocal')
    def test_get_user_by_phone_not_found(self, mock_session_local):
        """测试根据手机号查找用户 - 未找到"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.get_user_by_phone("19999999999")

        assert result is None

    # ==================== get_user_by_username 测试 ====================

    @patch('src.services.user_service.SessionLocal')
    def test_get_user_by_username_found(self, mock_session_local):
        """测试根据用户名查找用户 - 找到"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="testuser",
            nickname="测试",
            email="test@example.com",
            phone="13800138000",
            password_hash="hash123",
            avatar="avatar.jpg",
            is_admin=False,
            created_at=datetime.now()
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.get_user_by_username("testuser")

        assert result is not None
        assert result.username == "testuser"

    @patch('src.services.user_service.SessionLocal')
    def test_get_user_by_username_not_found(self, mock_session_local):
        """测试根据用户名查找用户 - 未找到"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.get_user_by_username("nonexistent")

        assert result is None

    # ==================== get_user_by_id 测试 ====================

    @patch('src.services.user_service.SessionLocal')
    def test_get_user_by_id_found(self, mock_session_local):
        """测试根据ID查找用户 - 找到"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="testuser",
            nickname="测试",
            email="test@example.com",
            phone="13800138000",
            password_hash="hash123",
            avatar="avatar.jpg",
            is_admin=False,
            created_at=datetime.now()
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.get_user_by_id("user123")

        assert result is not None
        assert result.user_id == "user123"

    @patch('src.services.user_service.SessionLocal')
    def test_get_user_by_id_not_found(self, mock_session_local):
        """测试根据ID查找用户 - 未找到"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.get_user_by_id("nonexistent-id")

        assert result is None

    # ==================== get_all_users 测试 ====================

    @patch('src.services.user_service.SessionLocal')
    def test_get_all_users_default_params(self, mock_session_local):
        """测试获取所有用户 - 默认参数"""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 100
        mock_db.query.return_value = mock_query

        # Mock 返回的用户列表
        mock_user_models = [
            MagicMock(
                user_id=f"user{i}",
                username=f"user{i}",
                nickname=None,
                email=f"user{i}@example.com",
                phone=None,
                password_hash="hash",
                avatar=None,
                is_admin=False,
                created_at=datetime.now()
            )
            for i in range(20)
        ]
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_user_models
        mock_session_local.return_value = mock_db

        service = UserService()
        users, total = service.get_all_users()

        assert total == 100
        assert len(users) == 20
        mock_query.filter.assert_not_called()  # 没有筛选条件

    @patch('src.services.user_service.SessionLocal')
    def test_get_all_users_with_pagination(self, mock_session_local):
        """测试获取所有用户 - 带分页"""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 50
        mock_db.query.return_value = mock_query

        mock_user_models = [
            MagicMock(
                user_id=f"user{i}",
                username=f"user{i}",
                nickname=None,
                email=f"user{i}@example.com",
                phone=None,
                password_hash="hash",
                avatar=None,
                is_admin=False,
                created_at=datetime.now()
            )
            for i in range(10)
        ]
        # 链式调用：order_by().offset().limit().all()
        mock_order_by = MagicMock()
        mock_offset = MagicMock()
        mock_limit = MagicMock()

        mock_order_by.return_value = mock_offset
        mock_offset.offset.return_value = mock_limit
        mock_limit.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_user_models

        mock_query.order_by = mock_order_by
        mock_session_local.return_value = mock_db

        service = UserService()
        users, total = service.get_all_users(page=2, page_size=10)

        assert total == 50
        assert len(users) == 10
        # 验证偏移量计算：(page-1) * page_size = (2-1) * 10 = 10
        mock_offset.offset.assert_called_with(10)
        mock_limit.limit.assert_called_with(10)

    @patch('src.services.user_service.SessionLocal')
    def test_get_all_users_filter_admins(self, mock_session_local):
        """测试获取所有用户 - 筛选管理员"""
        mock_db = MagicMock()
        mock_query = MagicMock()
        # 创建新的查询对象用于筛选后的count
        mock_filtered_query = MagicMock()
        mock_filtered_query.count.return_value = 5
        mock_query.filter.return_value = mock_filtered_query
        mock_db.query.return_value = mock_query

        mock_user_models = [
            MagicMock(
                user_id=f"admin{i}",
                username=f"admin{i}",
                nickname=None,
                email=f"admin{i}@example.com",
                phone=None,
                password_hash="hash",
                avatar=None,
                is_admin=True,
                created_at=datetime.now()
            )
            for i in range(5)
        ]

        # 链式调用
        mock_order_by = MagicMock()
        mock_offset = MagicMock()
        mock_limit = MagicMock()

        mock_order_by.return_value = mock_offset
        mock_offset.offset.return_value = mock_limit
        mock_limit.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_user_models

        mock_filtered_query.order_by = mock_order_by
        mock_session_local.return_value = mock_db

        service = UserService()
        users, total = service.get_all_users(is_admin=True)

        assert total == 5
        assert len(users) == 5
        assert all(u.is_admin for u in users)
        mock_query.filter.assert_called_once()

    @patch('src.services.user_service.SessionLocal')
    def test_get_all_users_filter_normal_users(self, mock_session_local):
        """测试获取所有用户 - 筛选普通用户"""
        mock_db = MagicMock()
        mock_query = MagicMock()
        # 创建新的查询对象用于筛选后的count
        mock_filtered_query = MagicMock()
        mock_filtered_query.count.return_value = 95
        mock_query.filter.return_value = mock_filtered_query
        mock_db.query.return_value = mock_query

        mock_user_models = [
            MagicMock(
                user_id=f"user{i}",
                username=f"user{i}",
                nickname=None,
                email=f"user{i}@example.com",
                phone=None,
                password_hash="hash",
                avatar=None,
                is_admin=False,
                created_at=datetime.now()
            )
            for i in range(20)
        ]

        # 链式调用
        mock_order_by = MagicMock()
        mock_offset = MagicMock()
        mock_limit = MagicMock()

        mock_order_by.return_value = mock_offset
        mock_offset.offset.return_value = mock_limit
        mock_limit.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_user_models

        mock_filtered_query.order_by = mock_order_by
        mock_session_local.return_value = mock_db

        service = UserService()
        users, total = service.get_all_users(is_admin=False)

        assert total == 95
        assert all(not u.is_admin for u in users)

    # ==================== update_user 测试 ====================

    @patch('src.services.user_service.SessionLocal')
    def test_update_user_success(self, mock_session_local):
        """测试成功更新用户"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="oldname",
            nickname="旧昵称",
            email="old@example.com",
            phone="13800000000",
            password_hash="hash",
            avatar=None,
            is_admin=False
        )
        # 所有冲突检查都返回None（没有冲突）
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        # 第一次调用返回用户，后续调用（冲突检查）返回None
        call_count = [0]

        def mock_filter_side_effect(*args, **kwargs):
            if call_count[0] == 0:
                call_count[0] += 1
                return MagicMock(first=MagicMock(return_value=mock_user_model))
            else:
                return MagicMock(first=MagicMock(return_value=None))

        mock_db.query.return_value.filter.side_effect = mock_filter_side_effect

        service = UserService()
        result = service.update_user(
            user_id="user123",
            username="newname",
            nickname="新昵称",
            email="new@example.com"
        )

        assert result is not None
        assert mock_user_model.username == "newname"
        assert mock_user_model.nickname == "新昵称"
        assert mock_user_model.email == "new@example.com"
        mock_db.commit.assert_called_once()

    @patch('src.services.user_service.SessionLocal')
    def test_update_user_not_found(self, mock_session_local):
        """测试更新不存在的用户"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.update_user("nonexistent-id", username="newname")

        assert result is None
        mock_db.commit.assert_not_called()

    @patch('src.services.user_service.SessionLocal')
    def test_update_user_duplicate_username(self, mock_session_local):
        """测试更新用户时用户名重复"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="oldname",
            nickname="旧昵称",
            email="old@example.com",
            phone=None,
            password_hash="hash",
            avatar=None,
            is_admin=False
        )
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_user_model,  # 第一次查询找到用户
            MagicMock()  # 第二次查询发现用户名已存在
        ]
        mock_session_local.return_value = mock_db

        service = UserService()

        with pytest.raises(ValueError, match="用户名已被其他用户使用"):
            service.update_user("user123", username="existingname")

    @patch('src.services.user_service.SessionLocal')
    def test_update_user_cannot_revoke_last_admin(self, mock_session_local):
        """测试不能取消最后一个管理员"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="admin",
            nickname="管理员",
            email="admin@example.com",
            phone=None,
            password_hash="hash",
            avatar=None,
            is_admin=True
        )
        mock_db.query.return_value.filter.return_value.count.return_value = 1  # 只有1个管理员
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()

        with pytest.raises(ValueError, match="不允许取消最后一个管理员的管理员权限"):
            service.update_user("user123", is_admin=False)

    @patch('src.services.user_service.SessionLocal')
    def test_update_user_can_revoke_admin_if_multiple(self, mock_session_local):
        """测试有多个管理员时可以取消一个"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="admin",
            nickname="管理员",
            email="admin@example.com",
            phone=None,
            password_hash="hash",
            avatar=None,
            is_admin=True
        )
        mock_db.query.return_value.filter.return_value.count.return_value = 2  # 有2个管理员
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.update_user("user123", is_admin=False)

        assert result is not None
        assert mock_user_model.is_admin is False
        mock_db.commit.assert_called_once()

    @patch('src.services.user_service.SessionLocal')
    def test_update_user_same_values_no_conflict(self, mock_session_local):
        """测试更新为相同的值不会产生冲突"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="testuser",
            nickname="测试",
            email="test@example.com",
            phone="13800138000",
            password_hash="hash",
            avatar=None,
            is_admin=False
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.update_user(
            "user123",
            username="testuser",  # 相同用户名
            email="test@example.com",  # 相同邮箱
            phone="13800138000"  # 相同手机号
        )

        assert result is not None
        mock_db.commit.assert_called_once()

    # ==================== delete_user 测试 ====================

    @patch('src.services.user_service.SessionLocal')
    def test_delete_user_success(self, mock_session_local):
        """测试成功删除用户"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="testuser",
            is_admin=False
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.delete_user("user123", "current-user-id")

        assert result is True
        mock_db.delete.assert_called_once_with(mock_user_model)
        mock_db.commit.assert_called_once()

    @patch('src.services.user_service.SessionLocal')
    def test_delete_user_not_found(self, mock_session_local):
        """测试删除不存在的用户"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.delete_user("nonexistent-id", "current-user-id")

        assert result is False
        mock_db.delete.assert_not_called()

    @patch('src.services.user_service.SessionLocal')
    def test_delete_user_cannot_delete_self(self, mock_session_local):
        """测试不能删除自己"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        service = UserService()

        with pytest.raises(ValueError, match="不允许删除自己"):
            service.delete_user("user123", "user123")

    @patch('src.services.user_service.SessionLocal')
    def test_delete_user_cannot_delete_last_admin(self, mock_session_local):
        """测试不能删除最后一个管理员"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="admin123",
            username="admin",
            is_admin=True
        )
        mock_db.query.return_value.filter.return_value.count.return_value = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()

        with pytest.raises(ValueError, match="不允许删除最后一个管理员"):
            service.delete_user("admin123", "current-user-id")

    @patch('src.services.user_service.SessionLocal')
    def test_delete_user_can_delete_admin_if_multiple(self, mock_session_local):
        """测试有多个管理员时可以删除一个管理员"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="admin123",
            username="admin",
            is_admin=True
        )
        mock_db.query.return_value.filter.return_value.count.return_value = 2
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.delete_user("admin123", "current-user-id")

        assert result is True
        mock_db.delete.assert_called_once()

    # ==================== reset_password 测试 ====================

    @patch('src.services.user_service.SessionLocal')
    def test_reset_password_success(self, mock_session_local):
        """测试成功重置密码"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="testuser",
            nickname=None,
            email="test@example.com",
            phone=None,
            password_hash="oldhash",
            avatar=None,
            is_admin=False,
            created_at=datetime.now()
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.reset_password("user123", "newpassword123")

        assert result is True
        assert mock_user_model.password_hash != "oldhash"
        assert len(mock_user_model.password_hash) > 0
        mock_db.commit.assert_called_once()

    @patch('src.services.user_service.SessionLocal')
    def test_reset_password_user_not_found(self, mock_session_local):
        """测试重置密码 - 用户不存在"""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.reset_password("nonexistent-id", "newpassword123")

        assert result is False
        mock_db.commit.assert_not_called()

    @patch('src.services.user_service.SessionLocal')
    def test_reset_password_too_short(self, mock_session_local):
        """测试重置密码 - 密码太短"""
        mock_session_local.return_value = MagicMock()

        service = UserService()

        with pytest.raises(ValueError, match="密码长度不能少于6位"):
            service.reset_password("user123", "12345")

    @patch('src.services.user_service.SessionLocal')
    def test_reset_password_exactly_6_chars(self, mock_session_local):
        """测试重置密码 - 密码刚好6位"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="testuser",
            nickname=None,
            email="test@example.com",
            phone=None,
            password_hash="oldhash",
            avatar=None,
            is_admin=False,
            created_at=datetime.now()
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        result = service.reset_password("user123", "123456")

        assert result is True
        mock_db.commit.assert_called_once()

    @patch('src.services.user_service.SessionLocal')
    def test_reset_password_long_password(self, mock_session_local):
        """测试重置密码 - 长密码"""
        mock_db = MagicMock()
        mock_user_model = MagicMock(
            user_id="user123",
            username="testuser",
            nickname=None,
            email="test@example.com",
            phone=None,
            password_hash="oldhash",
            avatar=None,
            is_admin=False,
            created_at=datetime.now()
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user_model
        mock_session_local.return_value = mock_db

        service = UserService()
        long_password = "a" * 100
        result = service.reset_password("user123", long_password)

        assert result is True
        mock_db.commit.assert_called_once()
