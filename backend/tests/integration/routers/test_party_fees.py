# -*- coding: utf-8 -*-
"""党费管理API集成测试（TDD）"""
import pytest
from sqlalchemy.orm import Session
from httpx import AsyncClient


class TestPartyFeesListAPI:
    """党费列表API测试"""

    @pytest.mark.asyncio
    async def test_获取党费列表_需要认证(self, async_client: AsyncClient):
        """RED: 测试未认证访问被拒绝"""
        response = await async_client.get("/api/v1/party/fees")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_获取党费列表_返回空列表_当数据库无记录时(self, admin_client: AsyncClient):
        """RED: 测试获取党费列表"""
        response = await admin_client.get("/api/v1/party/fees")
        assert response.status_code == 200
        data = response.json()
        assert "fees" in data
        assert "total" in data
        assert data["total"] == 0


class TestCreatePartyFeeAPI:
    """创建党费API测试"""

    @pytest.mark.asyncio
    async def test_创建党费_成功_当提供完整信息时(self, admin_client: AsyncClient):
        """RED: 测试创建党费"""
        from datetime import datetime

        fee_data = {
            "member_id": "test-member-id",
            "member_name": "张三",
            "amount": "50.00",
            "payment_date": datetime.now().isoformat(),
            "payment_method": "现金",
            "fee_month": "2026-03",
            "status": "已缴"
        }

        response = await admin_client.post(
            "/api/v1/party/fees",
            json=fee_data
        )

        assert response.status_code == 201
        data = response.json()
        assert "fee_id" in data
        assert data["member_name"] == "张三"

    @pytest.mark.asyncio
    async def test_创建党费_失败_当缺少必填字段时(self, admin_client: AsyncClient):
        """RED: 测试创建党费 - 缺少必填字段"""
        incomplete_data = {
            "member_name": "李四"
        }

        response = await admin_client.post(
            "/api/v1/party/fees",
            json=incomplete_data
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_创建党费_成功_当没有member_id时(self, admin_client: AsyncClient):
        """RED: 测试创建党费 - 前端只提供党员姓名不提供member_id"""
        from datetime import datetime

        fee_data = {
            "member_name": "王五",
            "amount": "100.00",
            "payment_date": datetime.now().isoformat(),
            "payment_method": "微信",
            "fee_month": "2026-03",
            "status": "已缴"
        }

        response = await admin_client.post(
            "/api/v1/party/fees",
            json=fee_data
        )

        assert response.status_code == 201
        data = response.json()
        assert "fee_id" in data
        assert data["member_name"] == "王五"
        # member_id应该是None
        assert data.get("member_id") is None or data.get("member_id") == ""

    @pytest.mark.asyncio
    async def test_创建党费_成功_当包含空字符串的可选字段时(self, admin_client: AsyncClient):
        """RED: 测试创建党费 - 前端发送空字符串的可选字段"""
        from datetime import datetime

        fee_data = {
            "member_name": "赵六",
            "amount": "75.50",
            "payment_date": datetime.now().isoformat(),
            "payment_method": "支付宝",
            "fee_month": "2026-03",
            "status": "已缴",
            "collector": "",  # 空字符串
            "remark": ""  # 空字符串
        }

        response = await admin_client.post(
            "/api/v1/party/fees",
            json=fee_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["member_name"] == "赵六"
        # 空字符串应该被转换为None
        assert data.get("collector") is None or data.get("collector") == ""
        assert data.get("remark") is None or data.get("remark") == ""


class TestGetPartyFeeDetailAPI:
    """党费详情API测试"""

    @pytest.mark.asyncio
    async def test_获取党费详情_成功_当记录存在时(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试获取党费详情"""
        from src.db_models_party import PartyFeeModel
        import uuid
        from datetime import datetime

        fee = PartyFeeModel(
            fee_id=str(uuid.uuid4()),
            member_id="test-member-id",
            member_name="测试党员",
            amount=50.00,
            payment_date=datetime.now(),
            payment_method="现金",
            fee_month="2026-03",
            status="已缴"
        )
        db_session.add(fee)
        db_session.commit()

        response = await admin_client.get(f"/api/v1/party/fees/{fee.fee_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["fee_id"] == fee.fee_id

    @pytest.mark.asyncio
    async def test_获取党费详情_404_当记录不存在时(self, admin_client: AsyncClient):
        """RED: 测试获取不存在的党费"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await admin_client.get(f"/api/v1/party/fees/{fake_id}")
        assert response.status_code == 404


class TestUpdatePartyFeeAPI:
    """更新党费API测试"""

    @pytest.mark.asyncio
    async def test_更新党费_成功_当数据有效时(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试更新党费"""
        from src.db_models_party import PartyFeeModel
        import uuid
        from datetime import datetime

        fee = PartyFeeModel(
            fee_id=str(uuid.uuid4()),
            member_id="test-member-id",
            member_name="张三",
            amount=50.00,
            payment_date=datetime.now(),
            payment_method="现金",
            fee_month="2026-03",
            status="已缴"
        )
        db_session.add(fee)
        db_session.commit()

        update_data = {"amount": "100.00"}
        response = await admin_client.patch(
            f"/api/v1/party/fees/{fee.fee_id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["amount"]) == 100.00


class TestDeletePartyFeeAPI:
    """删除党费API测试"""

    @pytest.mark.asyncio
    async def test_删除党费_成功_当记录存在时(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试删除党费"""
        from src.db_models_party import PartyFeeModel
        import uuid
        from datetime import datetime

        fee = PartyFeeModel(
            fee_id=str(uuid.uuid4()),
            member_id="test-member-id",
            member_name="张三",
            amount=50.00,
            payment_date=datetime.now(),
            payment_method="现金",
            fee_month="2026-03",
            status="已缴"
        )
        db_session.add(fee)
        db_session.commit()

        response = await admin_client.delete(f"/api/v1/party/fees/{fee.fee_id}")

        assert response.status_code == 204

        # 验证已删除
        get_response = await admin_client.get(f"/api/v1/party/fees/{fee.fee_id}")
        assert get_response.status_code == 404
