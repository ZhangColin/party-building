# -*- coding: utf-8 -*-
"""测试工具列表路由"""
import pytest


@pytest.mark.asyncio
async def test_get_all_tools(logged_in_client):
    """测试获取所有工具"""
    response = await logged_in_client.get("/api/v1/tools")

    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert isinstance(data["categories"], list)


@pytest.mark.asyncio
async def test_get_all_tools_response_structure(logged_in_client):
    """测试工具响应结构"""
    response = await logged_in_client.get("/api/v1/tools")

    assert response.status_code == 200
    data = response.json()

    # 验证响应结构
    assert isinstance(data, dict)
    assert "categories" in data
    assert isinstance(data["categories"], list)

    # 如果有分类，验证分类结构
    if len(data["categories"]) > 0:
        category = data["categories"][0]
        # category可能有不同的键名，检查是否有"category"或"name"
        assert "category" in category or "name" in category
        assert "tools" in category
        assert isinstance(category["tools"], list)


@pytest.mark.asyncio
async def test_get_all_tools_without_auth(async_client):
    """测试未认证用户获取工具列表"""
    response = await async_client.get("/api/v1/tools")

    # 应该返回401未认证
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_tools_by_toolset(logged_in_client):
    """测试按工具集获取工具"""
    response = await logged_in_client.get("/api/v1/toolsets/text_gen/tools")

    # 可能返回200（工具集存在）或404（工具集不存在）
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)


@pytest.mark.asyncio
async def test_get_tools_by_nonexistent_toolset(logged_in_client):
    """测试获取不存在的工具集"""
    response = await logged_in_client.get("/api/v1/toolsets/nonexistent_toolset/tools")

    # 应该返回200但categories为空
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert isinstance(data["categories"], list)


@pytest.mark.asyncio
async def test_tools_filter_visible_only(logged_in_client):
    """测试只返回可见工具"""
    response = await logged_in_client.get("/api/v1/tools")

    assert response.status_code == 200
    data = response.json()

    # 验证所有工具都是可见的
    for category in data["categories"]:
        for tool in category["tools"]:
            assert tool["visible"] is True
