# -*- coding: utf-8 -*-
"""JWT密钥验证单元测试"""

import os
import pytest
from src.services.auth_service import AuthService


class TestJWTSecretValidation:
    """JWT密钥验证测试"""

    def test_init_with_valid_secret(self):
        """测试使用有效密钥初始化"""
        # 临时设置有效的JWT密钥
        original_key = os.environ.get("JWT_SECRET_KEY")
        try:
            os.environ["JWT_SECRET_KEY"] = "a" * 32  # 32字符
            service = AuthService()
            assert service.secret_key == "a" * 32
            assert service.algorithm == "HS256"
        finally:
            # 恢复原值
            if original_key is None:
                os.environ.pop("JWT_SECRET_KEY", None)
            else:
                os.environ["JWT_SECRET_KEY"] = original_key

    def test_init_without_secret_raises_error(self):
        """测试未设置JWT密钥时抛出异常"""
        # 临时移除JWT密钥
        original_key = os.environ.get("JWT_SECRET_KEY")
        try:
            os.environ.pop("JWT_SECRET_KEY", None)

            # 应该抛出RuntimeError
            with pytest.raises(RuntimeError) as exc_info:
                AuthService()

            # 验证错误消息
            assert "JWT_SECRET_KEY" in str(exc_info.value)
            assert "required" in str(exc_info.value)
        finally:
            # 恢复原值
            if original_key is not None:
                os.environ["JWT_SECRET_KEY"] = original_key

    def test_init_with_short_secret_raises_error(self):
        """测试密钥长度不足时抛出异常"""
        # 临时设置短密钥
        original_key = os.environ.get("JWT_SECRET_KEY")
        try:
            os.environ["JWT_SECRET_KEY"] = "short"  # 5字符 < 32

            # 应该抛出ValueError
            with pytest.raises(ValueError) as exc_info:
                AuthService()

            # 验证错误消息
            assert "32 characters" in str(exc_info.value)
            assert "5" in str(exc_info.value)  # 当前长度
        finally:
            # 恢复原值
            if original_key is None:
                os.environ.pop("JWT_SECRET_KEY", None)
            else:
                os.environ["JWT_SECRET_KEY"] = original_key

    def test_init_with_exactly_32_chars(self):
        """测试正好32字符的密钥可以接受"""
        original_key = os.environ.get("JWT_SECRET_KEY")
        try:
            os.environ["JWT_SECRET_KEY"] = "a" * 32
            service = AuthService()
            assert service.secret_key == "a" * 32
        finally:
            if original_key is None:
                os.environ.pop("JWT_SECRET_KEY", None)
            else:
                os.environ["JWT_SECRET_KEY"] = original_key

    def test_init_with_longer_secret(self):
        """测试超过32字符的密钥可以接受"""
        original_key = os.environ.get("JWT_SECRET_KEY")
        try:
            os.environ["JWT_SECRET_KEY"] = "a" * 64
            service = AuthService()
            assert service.secret_key == "a" * 64
        finally:
            if original_key is None:
                os.environ.pop("JWT_SECRET_KEY", None)
            else:
                os.environ["JWT_SECRET_KEY"] = original_key
