# -*- coding: utf-8 -*-
"""
测试常用工具分类 API 端点

测试 GET /api/v1/common-tools/categories 端点
"""

import pytest
from httpx import AsyncClient


class TestCommonToolsCategoriesAPI:
    """测试常用工具分类 API"""

    @pytest.mark.asyncio
    async def test_get_common_tool_categories_success(self, async_client: AsyncClient):
        """
        测试成功获取常用工具分类列表

        Given: 系统中存在工具分类和工具
        When: 客户端请求 GET /api/v1/common-tools/categories
        Then: 应该返回 200 状态码和分类列表
        """
        # When: 请求分类列表
        response = await async_client.get("/api/v1/common-tools/categories")

        # Then: 验证响应
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "categories" in data, "Response should contain 'categories' key"

        # 验证分类结构
        categories = data["categories"]
        assert isinstance(categories, list), "Categories should be a list"

        # 如果有数据，验证分类结构
        if len(categories) > 0:
            category = categories[0]
            assert "id" in category, "Category should have 'id'"
            assert "name" in category, "Category should have 'name'"
            assert "order" in category, "Category should have 'order'"
            assert "tools" in category, "Category should have 'tools'"
            assert isinstance(category["tools"], list), "Tools should be a list"

    @pytest.mark.asyncio
    async def test_get_common_tool_categories_empty(self, async_client: AsyncClient):
        """
        测试空分类列表的响应

        Given: 系统中没有工具分类
        When: 客户端请求 GET /api/v1/common-tools/categories
        Then: 应该返回 200 状态码和空的分类列表
        """
        # When: 请求分类列表
        response = await async_client.get("/api/v1/common-tools/categories")

        # Then: 验证响应
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        # 即使是空的，也应该是有效的列表结构
        assert isinstance(data["categories"], list)
