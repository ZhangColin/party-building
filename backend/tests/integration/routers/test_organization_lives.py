# -*- coding: utf-8 -*-
"""组织生活API集成测试（TDD）

按照TDD原则，先写失败的测试，然后实现功能。
"""
import pytest
from sqlalchemy.orm import Session
from httpx import AsyncClient


class TestOrganizationLivesListAPI:
    """组织生活列表API测试"""

    @pytest.mark.asyncio
    async def test_获取组织生活列表_需要认证(self, async_client: AsyncClient):
        """RED: 测试未认证访问被拒绝"""
        response = await async_client.get("/api/v1/party/organization-lives")

        # 应该返回401，因为需要认证
        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_获取组织生活列表_返回空列表_当数据库无记录时(self, admin_client: AsyncClient):
        """RED: 测试获取组织生活列表 - 预期行为：空列表返回200状态码"""
        response = await admin_client.get("/api/v1/party/organization-lives")

        # 应该返回200，即使没有数据
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert "total" in data
        assert data["total"] == 0
        assert data["records"] == []


class TestCreateOrganizationLifeAPI:
    """创建组织生活API测试"""

    @pytest.mark.asyncio
    async def test_创建组织生活_成功_当提供完整信息时(self, admin_client: AsyncClient):
        """RED: 测试创建组织生活 - 预期行为：成功创建返回201"""
        from datetime import datetime

        life_data = {
            "activity_type": "三会一课",
            "title": "支部党员大会",
            "activity_date": datetime.now().isoformat(),
            "location": "会议室A",
            "participants_count": 25,
            "content": "讨论支部工作计划",
            "organizer": "张书记"
        }

        response = await admin_client.post(
            "/api/v1/party/organization-lives",
            json=life_data
        )

        # 预期：创建成功
        assert response.status_code == 201
        data = response.json()
        assert "life_id" in data
        assert data["title"] == "支部党员大会"
        assert data["activity_type"] == "三会一课"

    @pytest.mark.asyncio
    async def test_创建组织生活_失败_当缺少必填字段时(self, admin_client: AsyncClient):
        """RED: 测试创建组织生活 - 缺少必填字段"""
        incomplete_data = {
            "title": "主题党日活动"
            # 缺少activity_type, activity_date等必填字段
        }

        response = await admin_client.post(
            "/api/v1/party/organization-lives",
            json=incomplete_data
        )

        # 预期：422验证错误
        assert response.status_code == 422
