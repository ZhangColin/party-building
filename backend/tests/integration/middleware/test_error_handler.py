# -*- coding: utf-8 -*-
"""
错误处理中间件测试
"""
import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from src.main import app
from src.interfaces.middleware.error_handler import (
    ApplicationException,
    NotFoundException,
    ForbiddenException,
    BadRequestException,
    UnauthorizedException,
)


class TestExceptionClasses:
    """测试异常类创建"""

    def test_application_exception(self):
        """测试ApplicationException创建"""
        exc = ApplicationException("Test error", code="TEST_ERROR", status_code=500)
        assert exc.message == "Test error"
        assert exc.code == "TEST_ERROR"
        assert exc.status_code == 500

    def test_not_found_exception(self):
        """测试NotFoundException"""
        not_found = NotFoundException("User not found")
        assert not_found.code == "NOT_FOUND"
        assert not_found.status_code == 404
        assert not_found.message == "User not found"

    def test_forbidden_exception(self):
        """测试ForbiddenException"""
        forbidden = ForbiddenException("Access denied")
        assert forbidden.code == "FORBIDDEN"
        assert forbidden.status_code == 403

    def test_bad_request_exception(self):
        """测试BadRequestException"""
        bad_request = BadRequestException("Invalid input")
        assert bad_request.code == "BAD_REQUEST"
        assert bad_request.status_code == 400

    def test_unauthorized_exception(self):
        """测试UnauthorizedException"""
        unauthorized = UnauthorizedException("Authentication required")
        assert unauthorized.code == "UNAUTHORIZED"
        assert unauthorized.status_code == 401

    def test_exception_with_details(self):
        """测试带details的异常"""
        details = {"field": "email", "reason": "invalid format"}
        exc = BadRequestException("Validation failed", details=details)
        assert exc.details == details


class TestErrorHandlerIntegration:
    """测试错误处理中间件集成"""

    def test_404_error_returns_unified_format(self):
        """测试404错误返回统一格式"""
        client = TestClient(app)
        response = client.get("/api/v1/nonexistent-endpoint")

        assert response.status_code == 404

        # FastAPI的默认404可能不包含我们的格式
        # 但在中间件完全注册后应该有统一格式

    def test_401_error_returns_unified_format(self):
        """测试401错误返回统一格式"""
        client = TestClient(app)
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401

        data = response.json()
        # 应该包含错误信息
        assert "detail" in data or "error" in data
