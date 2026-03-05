# -*- coding: utf-8 -*-
"""
临时文件API集成测试

测试 POST /api/v1/temp-files/upload 端点
"""
import pytest
import io
from httpx import AsyncClient


class TestTempFilesUploadAPI:
    """测试临时文件上传API"""

    @pytest.mark.asyncio
    async def test_upload_temp_file_success(self, async_client: AsyncClient):
        """
        测试成功上传临时文件

        Given: 存在有效的文本文件
        When: 客户端请求 POST /api/v1/temp-files/upload
        Then: 应该返回 200 状态码和临时文件信息
        """
        # Given: 创建测试文件
        file_content = b"test file content for upload"
        file_data = io.BytesIO(file_content)

        # When: 上传文件
        response = await async_client.post(
            "/api/v1/temp-files/upload",
            files={"file": ("test.txt", file_data, "text/plain")}
        )

        # Then: 验证响应
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()
        assert "temp_id" in data, "Response should contain 'temp_id'"
        assert data["filename"] == "test.txt"
        assert data["size"] == len(file_content)
        assert data["content_preview"] == "test file content for upload"

    @pytest.mark.asyncio
    async def test_upload_file_too_large(self, async_client: AsyncClient):
        """
        测试上传超大文件

        Given: 文件大小超过10MB限制
        When: 客户端请求 POST /api/v1/temp-files/upload
        Then: 应该返回 400 状态码和错误信息
        """
        # Given: 创建超过限制的文件（11MB）
        large_content = b"x" * (11 * 1024 * 1024)
        file_data = io.BytesIO(large_content)

        # When: 上传超大文件
        response = await async_client.post(
            "/api/v1/temp-files/upload",
            files={"file": ("large.txt", file_data, "text/plain")}
        )

        # Then: 验证响应
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "文件大小超过限制" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_file_no_file(self, async_client: AsyncClient):
        """
        测试没有文件的上传

        Given: 请求中没有文件
        When: 客户端请求 POST /api/v1/temp-files/upload
        Then: 应该返回 422 状态码（验证错误）
        """
        # When: 发送没有文件的请求
        response = await async_client.post("/api/v1/temp-files/upload")

        # Then: 验证响应
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_upload_chinese_filename(self, async_client: AsyncClient):
        """
        测试上传中文文件名

        Given: 存在中文文件名的文件
        When: 客户端请求 POST /api/v1/temp-files/upload
        Then: 应该返回 200 状态码并正确处理中文文件名
        """
        # Given: 创建测试文件
        file_content = "测试文件内容".encode('utf-8')
        file_data = io.BytesIO(file_content)

        # When: 上传文件
        response = await async_client.post(
            "/api/v1/temp-files/upload",
            files={"file": ("测试文档.txt", file_data, "text/plain")}
        )

        # Then: 验证响应
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["filename"] == "测试文档.txt"
        assert data["size"] == len(file_content)
        assert data["content_preview"] == "测试文件内容"

    @pytest.mark.asyncio
    async def test_upload_binary_file(self, async_client: AsyncClient):
        """
        测试上传二进制文件

        Given: 存在二进制文件（如图片）
        When: 客户端请求 POST /api/v1/temp-files/upload
        Then: 应该返回 200 状态码，content_preview 可能为 None
        """
        # Given: 创建测试二进制文件
        file_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00"  # PNG 文件头
        file_data = io.BytesIO(file_content)

        # When: 上传文件
        response = await async_client.post(
            "/api/v1/temp-files/upload",
            files={"file": ("image.png", file_data, "image/png")}
        )

        # Then: 验证响应
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data["filename"] == "image.png"
        assert data["size"] == len(file_content)
        # 二进制文件的 content_preview 可能为 None
        assert data["content_preview"] is None or isinstance(data["content_preview"], str)
