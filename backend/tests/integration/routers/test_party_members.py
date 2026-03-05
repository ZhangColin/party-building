# -*- coding: utf-8 -*-
"""党员管理API集成测试（TDD）

按照TDD原则，先写失败的测试，然后实现功能。
"""
import pytest
from sqlalchemy.orm import Session
from httpx import AsyncClient


class TestPartyMembersListAPI:
    """党员列表API测试"""

    @pytest.mark.asyncio
    async def test_获取党员列表_返回空列表_当数据库无记录时(self, admin_client: AsyncClient):
        """RED: 测试获取党员列表 - 预期行为：空列表返回200状态码"""
        response = await admin_client.get(
            "/api/v1/party/members"
        )

        # 应该返回200，即使没有数据
        assert response.status_code == 200
        data = response.json()
        assert "members" in data
        assert "total" in data
        assert data["total"] == 0
        assert data["members"] == []

    @pytest.mark.asyncio
    async def test_获取党员列表_需要认证(self, async_client: AsyncClient):
        """RED: 测试未认证访问被拒绝"""
        response = await async_client.get("/api/v1/party/members")

        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_获取党员列表_分页正常_当有25条数据时(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试分页功能"""
        from src.db_models_party import PartyMemberModel
        import uuid
        from datetime import date

        # 创建25条测试数据
        for i in range(25):
            member = PartyMemberModel(
                member_id=str(uuid.uuid4()),
                name=f"测试党员{i}",
                gender="男",
                birth_date=date(1990, 1, 1),
                join_date=date(2020, 7, 1),
                party_branch="第一党支部",
                member_type="正式党员",
                status="正常"
            )
            db_session.add(member)
        db_session.commit()

        # 请求第一页，每页20条
        response = await admin_client.get(
            "/api/v1/party/members?page=1&page_size=20"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert len(data["members"]) == 20

    @pytest.mark.asyncio
    async def test_获取党员列表_按支部筛选_正常工作(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试按党支部筛选"""
        from src.db_models_party import PartyMemberModel
        import uuid
        from datetime import date

        # 创建不同支部的党员
        for branch in ["第一党支部", "第二党支部", "第一党支部"]:
            member = PartyMemberModel(
                member_id=str(uuid.uuid4()),
                name=f"测试党员{branch}",
                gender="男",
                birth_date=date(1990, 1, 1),
                join_date=date(2020, 7, 1),
                party_branch=branch,
                member_type="正式党员",
                status="正常"
            )
            db_session.add(member)
        db_session.commit()

        # 筛选第一党支部
        response = await admin_client.get(
            "/api/v1/party/members?party_branch=第一党支部"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert all(m["party_branch"] == "第一党支部" for m in data["members"])


class TestCreatePartyMemberAPI:
    """创建党员API测试"""

    @pytest.mark.asyncio
    async def test_创建党员_成功_当提供完整信息时(self, admin_client: AsyncClient):
        """RED: 测试创建党员 - 预期行为：成功创建返回201"""
        member_data = {
            "name": "张三",
            "gender": "男",
            "birth_date": "1990-01-01",
            "join_date": "2020-07-01",
            "party_branch": "第一党支部",
            "member_type": "正式党员",
            "phone": "13800138000",
            "email": "zhangsan@example.com"
        }

        response = await admin_client.post(
            "/api/v1/party/members",
            json=member_data
        )

        # 预期：创建成功
        assert response.status_code == 201
        data = response.json()
        assert "member_id" in data
        assert data["name"] == "张三"
        assert data["gender"] == "男"

    @pytest.mark.asyncio
    async def test_创建党员_失败_当缺少必填字段时(self, admin_client: AsyncClient):
        """RED: 测试创建党员 - 缺少必填字段"""
        incomplete_data = {
            "name": "李四"
            # 缺少gender, birth_date, join_date, party_branch等必填字段
        }

        response = await admin_client.post(
            "/api/v1/party/members",
            json=incomplete_data
        )

        # 预期：422验证错误
        assert response.status_code == 422


class TestGetPartyMemberDetailAPI:
    """党员详情API测试"""

    @pytest.mark.asyncio
    async def test_获取党员详情_成功_当党员存在时(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试获取党员详情"""
        # 先创建一个党员
        from src.db_models_party import PartyMemberModel
        import uuid
        from datetime import date

        member = PartyMemberModel(
            member_id=str(uuid.uuid4()),
            name="测试党员",
            gender="男",
            birth_date=date(1990, 1, 1),
            join_date=date(2020, 7, 1),
            party_branch="测试支部",
            member_type="正式党员",
            status="正常"
        )
        db_session.add(member)
        db_session.commit()

        # 获取详情
        response = await admin_client.get(
            f"/api/v1/party/members/{member.member_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["member_id"] == member.member_id
        assert data["name"] == "测试党员"

    @pytest.mark.asyncio
    async def test_获取党员详情_404_当党员不存在时(self, admin_client: AsyncClient):
        """RED: 测试获取不存在党员的详情"""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = await admin_client.get(
            f"/api/v1/party/members/{fake_id}"
        )

        assert response.status_code == 404


class TestUpdatePartyMemberAPI:
    """更新党员API测试"""

    @pytest.mark.asyncio
    async def test_更新党员_成功_当数据有效时(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试更新党员信息"""
        from src.db_models_party import PartyMemberModel
        import uuid
        from datetime import date

        # 先创建党员
        member = PartyMemberModel(
            member_id=str(uuid.uuid4()),
            name="王五",
            gender="男",
            birth_date=date(1990, 1, 1),
            join_date=date(2020, 7, 1),
            party_branch="第一党支部",
            member_type="正式党员",
            status="正常"
        )
        db_session.add(member)
        db_session.commit()

        # 更新手机号
        update_data = {
            "phone": "13900139000"
        }

        response = await admin_client.patch(
            f"/api/v1/party/members/{member.member_id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "13900139000"


class TestDeletePartyMemberAPI:
    """删除党员API测试"""

    @pytest.mark.asyncio
    async def test_删除党员_成功_当党员存在时(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试删除党员"""
        from src.db_models_party import PartyMemberModel
        import uuid
        from datetime import date

        # 先创建党员
        member = PartyMemberModel(
            member_id=str(uuid.uuid4()),
            name="赵六",
            gender="女",
            birth_date=date(1992, 5, 15),
            join_date=date(2021, 7, 1),
            party_branch="第二党支部",
            member_type="正式党员",
            status="正常"
        )
        db_session.add(member)
        db_session.commit()

        # 删除
        response = await admin_client.delete(
            f"/api/v1/party/members/{member.member_id}"
        )

        assert response.status_code == 204

        # 验证已删除
        get_response = await admin_client.get(
            f"/api/v1/party/members/{member.member_id}"
        )
        assert get_response.status_code == 404
