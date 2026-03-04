# -*- coding: utf-8 -*-
"""AuthService 单元测试"""
import pytest
from datetime import datetime, timedelta
from src.services.auth_service import AuthService
from src.models import User


class TestAuthService:
    """AuthService 测试类"""

    def test_init_with_default_secret_raises_error(self, monkeypatch):
        """测试未设置密钥时抛出异常"""
        # 确保环境变量未设置
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

        # 应该抛出RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            AuthService()

        assert "JWT_SECRET_KEY" in str(exc_info.value)
        assert "required" in str(exc_info.value)

    def test_init_with_short_secret_raises_error(self, monkeypatch):
        """测试密钥过短时抛出异常"""
        # 设置短密钥（<32字符）
        monkeypatch.setenv("JWT_SECRET_KEY", "my-custom-secret")

        # 应该抛出ValueError
        with pytest.raises(ValueError) as exc_info:
            AuthService()

        assert "32 characters" in str(exc_info.value)

    def test_init_with_valid_custom_secret(self, monkeypatch):
        """测试使用有效的自定义密钥初始化（至少32字符）"""
        # 设置有效的32字符密钥
        valid_secret = "a" * 32
        monkeypatch.setenv("JWT_SECRET_KEY", valid_secret)

        service = AuthService()

        assert service.secret_key == valid_secret
        assert service.algorithm == "HS256"

    def test_generate_token_default_expiry(self, monkeypatch):
        """测试生成 token（默认24小时过期）"""
        # 设置32字符密钥
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
        service = AuthService()
        user = User.create(username="testuser", password="password123", email="test@example.com")

        token = service.generate_token(user)

        assert isinstance(token, str)
        assert len(token) > 50

        # 验证 token 可以被解析
        payload = service.verify_token(token)
        assert payload is not None
        assert payload["user_id"] == user.user_id
        assert "exp" in payload
        assert "iat" in payload

        # 验证过期时间约为24小时后
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        time_diff = exp_time - iat_time
        assert time_diff.total_seconds() == pytest.approx(24 * 3600, abs=60)

    def test_generate_token_with_remember_me(self, monkeypatch):
        """测试生成 token（记住我 - 7天过期）"""
        # 设置32字符密钥
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
        service = AuthService()
        user = User.create(username="testuser", password="password123", email="test@example.com")

        token = service.generate_token(user, remember_me=True)

        payload = service.verify_token(token)
        assert payload is not None

        # 验证过期时间约为7天后
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        time_diff = exp_time - iat_time
        assert time_diff.total_seconds() == pytest.approx(7 * 24 * 3600, abs=60)

    def test_verify_token_valid(self, monkeypatch):
        """测试验证有效 token"""
        # 设置32字符密钥
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
        service = AuthService()
        user = User.create(username="testuser", password="password123", email="test@example.com")
        token = service.generate_token(user)

        payload = service.verify_token(token)

        assert payload is not None
        assert payload["user_id"] == user.user_id
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_token_invalid(self, monkeypatch):
        """测试验证无效 token"""
        # 设置32字符密钥
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
        service = AuthService()

        payload = service.verify_token("invalid-token")

        assert payload is None

    def test_verify_token_expired(self, monkeypatch):
        """测试验证过期 token"""
        # 使用32字符的密钥（符合新要求）
        test_secret = "a" * 32
        monkeypatch.setenv("JWT_SECRET_KEY", test_secret)

        # 手动创建一个过期的 token
        from jose import jwt
        import time

        payload = {
            "user_id": "test-user-id",
            "exp": int(time.time()) - 3600,  # 1小时前过期
            "iat": int(time.time()) - 7200   # 2小时前签发
        }
        expired_token = jwt.encode(payload, test_secret, algorithm="HS256")

        service = AuthService()
        result = service.verify_token(expired_token)

        assert result is None

    def test_verify_token_malformed(self, monkeypatch):
        """测试验证格式错误的 token"""
        # 设置32字符密钥
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
        service = AuthService()

        # 测试各种格式错误的 token
        assert service.verify_token("") is None
        assert service.verify_token("not.a.token") is None
        assert service.verify_token("Bearer token") is None

    def test_get_user_id_from_token_valid(self, monkeypatch):
        """测试从有效 token 获取用户 ID"""
        # 设置32字符密钥
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
        service = AuthService()
        user = User.create(username="testuser", password="password123", email="test@example.com")
        token = service.generate_token(user)

        user_id = service.get_user_id_from_token(token)

        assert user_id == user.user_id

    def test_get_user_id_from_token_invalid(self, monkeypatch):
        """测试从无效 token 获取用户 ID"""
        # 设置32字符密钥
        monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
        service = AuthService()

        user_id = service.get_user_id_from_token("invalid-token")

        assert user_id is None
