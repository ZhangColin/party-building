# 党建CRUD功能TDD完善实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 通过TDD方式完善党员管理、组织生活、党费管理三个模块的CRUD功能，确保列表查询、数据添加、编辑更新、数据库适配四大问题全部解决。

**Architecture:** 采用逐模块完整TDD方法，每个模块先写集成测试发现bug，然后修复代码直到所有测试通过。只写API集成测试，不写Service单元测试，保持简单高效。

**Tech Stack:** pytest, httpx (AsyncClient), SQLAlchemy, FastAPI, Pydantic

---

## 阶段1：党员管理模块TDD完善

### Task 1: 补全党员列表查询测试

**Files:**
- Modify: `backend/tests/integration/routers/test_party_members.py`

**Step 1: 添加分页测试到现有测试类**

```python
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
```

**Step 2: 运行测试验证**

Run: `cd backend && pytest tests/integration/routers/test_party_members.py::TestPartyMembersListAPI::test_获取党员列表_分页正常_当有25条数据时 -v`
Expected: FAIL 或 PASS（如果分页已实现）

**Step 3: 如果测试失败，检查Service层实现**

检查 `backend/src/services/party_member_service.py` 中的 `list_members` 方法确保正确实现分页逻辑。

**Step 4: 运行所有党员列表测试**

Run: `cd backend && pytest tests/integration/routers/test_party_members.py::TestPartyMembersListAPI -v`
Expected: 全部 PASS

**Step 5: 提交**

```bash
git add backend/tests/integration/routers/test_party_members.py
git commit -m "test(party): 添加党员列表分页测试"
```

---

### Task 2: 添加党员列表筛选测试

**Files:**
- Modify: `backend/tests/integration/routers/test_party_members.py`

**Step 1: 添加筛选测试**

```python
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
```

**Step 2: 运行测试**

Run: `cd backend && pytest tests/integration/routers/test_party_members.py::TestPartyMembersListAPI::test_获取党员列表_按支部筛选_正常工作 -v`
Expected: FAIL 或 PASS

**Step 3: 如果失败，修复筛选逻辑**

确保 `party_member_service.py` 中的筛选参数正确传递给查询。

**Step 4: 运行所有列表测试**

Run: `cd backend && pytest tests/integration/routers/test_party_members.py::TestPartyMembersListAPI -v`
Expected: 全部 PASS

**Step 5: 提交**

```bash
git add backend/tests/integration/routers/test_party_members.py backend/src/services/party_member_service.py
git commit -m "test(party): 添加党员列表筛选测试并修复"
```

---

### Task 3: 添加党员创建验证测试

**Files:**
- Modify: `backend/tests/integration/routers/test_party_members.py`

**Step 1: 添加身份证号格式验证测试**

```python
async def test_创建党员_失败_当身份证号格式错误时(self, admin_client: AsyncClient):
    """RED: 测试身份证号格式验证"""
    member_data = {
        "name": "张三",
        "gender": "男",
        "birth_date": "1990-01-01",
        "join_date": "2020-07-01",
        "party_branch": "第一党支部",
        "member_type": "正式党员",
        "id_card": "123456"  # 错误格式
    }

    response = await admin_client.post(
        "/api/v1/party/members",
        json=member_data
    )

    assert response.status_code == 422
```

**Step 2: 运行测试**

Run: `cd backend && pytest tests/integration/routers/test_party_members.py::TestCreatePartyMemberAPI::test_创建党员_失败_当身份证号格式错误时 -v`
Expected: FAIL 或 PASS

**Step 3: 如果失败，添加Pydantic验证**

在 `backend/src/models_party.py` 的 `PartyMemberCreate` 模型中添加：

```python
from pydantic import field_validator

@field_validator('id_card')
def validate_id_card(cls, v):
    if v and len(v) != 18:
        raise ValueError('身份证号必须为18位')
    return v
```

**Step 4: 运行所有创建测试**

Run: `cd backend && pytest tests/integration/routers/test_party_members.py::TestCreatePartyMemberAPI -v`
Expected: 全部 PASS

**Step 5: 提交**

```bash
git add backend/tests/integration/routers/test_party_members.py backend/src/models_party.py
git commit -m "test(party): 添加党员创建身份证号验证测试"
```

---

### Task 4: 运行所有党员管理测试并修复

**Step 1: 运行所有党员测试**

Run: `cd backend && pytest tests/integration/routers/test_party_members.py -v`
Expected: 记录失败的测试

**Step 2: 逐个修复失败的测试**

- 查看失败信息
- 定位问题代码
- 修复实现
- 单独运行该测试验证

**Step 3: 确保所有测试通过**

Run: `cd backend && pytest tests/integration/routers/test_party_members.py -v`
Expected: 全部 PASS

**Step 4: 提交所有修复**

```bash
git add backend/tests/integration/routers/test_party_members.py backend/src/services/party_member_service.py backend/src/models_party.py
git commit -m "test(party): 确保所有党员管理测试通过"
```

---

## 阶段2：组织生活模块TDD完善

### Task 5: 创建组织生活完整测试套件

**Files:**
- Modify: `backend/tests/integration/routers/test_organization_lives.py`

**Step 1: 添加组织生活更新测试**

```python
class TestUpdateOrganizationLifeAPI:
    """更新组织生活API测试"""

    @pytest.mark.asyncio
    async def test_更新组织生活_成功_当数据有效时(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试更新组织生活"""
        from src.db_models_party import OrganizationLifeModel
        import uuid
        from datetime import datetime

        # 先创建组织生活
        life = OrganizationLifeModel(
            life_id=str(uuid.uuid4()),
            activity_type="三会一课",
            title="原始标题",
            activity_date=datetime.now(),
            participants_count=20,
            organizer="张书记"
        )
        db_session.add(life)
        db_session.commit()

        # 更新
        update_data = {
            "title": "新标题",
            "content": "更新的内容"
        }

        response = await admin_client.patch(
            f"/api/v1/party/organization-lives/{life.life_id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "新标题"

    @pytest.mark.asyncio
    async def test_更新组织生活_404_当记录不存在时(self, admin_client: AsyncClient):
        """RED: 测试更新不存在的记录"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"title": "新标题"}

        response = await admin_client.patch(
            f"/api/v1/party/organization-lives/{fake_id}",
            json=update_data
        )

        assert response.status_code == 404
```

**Step 2: 运行测试**

Run: `cd backend && pytest tests/integration/routers/test_organization_lives.py::TestUpdateOrganizationLifeAPI -v`
Expected: FAIL（更新功能可能未实现）

**Step 3: 检查Service层更新方法**

检查 `backend/src/services/organization_life_service.py` 是否有 `update_record` 方法。

**Step 4: 如果需要，实现更新方法**

参考党员管理的更新实现：

```python
def update_record(self, life_id: str, **kwargs) -> Optional[Dict]:
    """更新组织生活记录"""
    from sqlalchemy import select

    stmt = select(OrganizationLifeModel).where(
        OrganizationLifeModel.life_id == life_id
    )
    result = self.db.execute(stmt).scalar_one_or_none()

    if not result:
        return None

    for key, value in kwargs.items():
        if hasattr(result, key) and value is not None:
            setattr(result, key, value)

    self.db.commit()
    self.db.refresh(result)

    return self._model_to_dict(result)
```

**Step 5: 运行测试验证**

Run: `cd backend && pytest tests/integration/routers/test_organization_lives.py::TestUpdateOrganizationLifeAPI -v`
Expected: PASS

**Step 6: 提交**

```bash
git add backend/tests/integration/routers/test_organization_lives.py backend/src/services/organization_life_service.py
git commit -m "test(party): 添加组织生活更新测试并实现"
```

---

### Task 6: 添加组织生活删除测试

**Files:**
- Modify: `backend/tests/integration/routers/test_organization_lives.py`

**Step 1: 添加删除测试**

```python
class TestDeleteOrganizationLifeAPI:
    """删除组织生活API测试"""

    @pytest.mark.asyncio
    async def test_删除组织生活_成功_当记录存在时(self, admin_client: AsyncClient, db_session: Session):
        """RED: 测试删除组织生活"""
        from src.db_models_party import OrganizationLifeModel
        import uuid
        from datetime import datetime

        # 先创建
        life = OrganizationLifeModel(
            life_id=str(uuid.uuid4()),
            activity_type="三会一课",
            title="待删除记录",
            activity_date=datetime.now(),
            participants_count=20,
            organizer="张书记"
        )
        db_session.add(life)
        db_session.commit()

        # 删除
        response = await admin_client.delete(
            f"/api/v1/party/organization-lives/{life.life_id}"
        )

        assert response.status_code == 204

        # 验证已删除
        get_response = await admin_client.get(
            f"/api/v1/party/organization-lives/{life.life_id}"
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_删除组织生活_404_当记录不存在时(self, admin_client: AsyncClient):
        """RED: 测试删除不存在的记录"""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = await admin_client.delete(
            f"/api/v1/party/organization-lives/{fake_id}"
        )

        assert response.status_code == 404
```

**Step 2: 运行测试**

Run: `cd backend && pytest tests/integration/routers/test_organization_lives.py::TestDeleteOrganizationLifeAPI -v`
Expected: FAIL 或 PASS

**Step 3: 运行所有组织生活测试**

Run: `cd backend && pytest tests/integration/routers/test_organization_lives.py -v`
Expected: 全部 PASS

**Step 4: 提交**

```bash
git add backend/tests/integration/routers/test_organization_lives.py
git commit -m "test(party): 添加组织生活删除测试"
```

---

## 阶段3：党费管理模块TDD完善

### Task 7: 创建党费管理完整测试套件

**Files:**
- Create: `backend/tests/integration/routers/test_party_fees.py`

**Step 1: 创建测试文件框架**

```python
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
```

**Step 2: 运行测试**

Run: `cd backend && pytest tests/integration/routers/test_party_fees.py -v`
Expected: 大部分 FAIL（党费功能可能未完全实现）

**Step 3: 逐个实现失败的测试**

根据测试失败信息，实现或修复 `party_fee_service.py` 中的对应方法。

**Step 4: 确保所有测试通过**

Run: `cd backend && pytest tests/integration/routers/test_party_fees.py -v`
Expected: 全部 PASS

**Step 5: 提交**

```bash
git add backend/tests/integration/routers/test_party_fees.py backend/src/services/party_fee_service.py
git commit -m "test(party): 添加党费管理完整测试套件"
```

---

## 阶段4：最终验证

### Task 8: 运行所有党建模块测试并修复

**Step 1: 运行所有党建模块测试**

Run: `cd backend && pytest tests/integration/routers/test_party*.py -v --tb=short`
Expected: 记录所有失败的测试

**Step 2: 修复所有失败的测试**

逐个修复：
- 查看失败原因
- 定位代码问题
- 修复实现
- 单独验证

**Step 3: 确保所有测试通过**

Run: `cd backend && pytest tests/integration/routers/test_party*.py -v`
Expected: 全部 PASS

**Step 4: 生成测试覆盖率报告**

Run: `cd backend && pytest tests/integration/routers/test_party*.py --cov=src/services/party_member_service --cov=src/services/organization_life_service --cov=src/services/party_fee_service --cov-report=term-missing`
Expected: 查看覆盖率报告

**Step 5: 最终提交**

```bash
git add backend/tests/integration/routers/test_party*.py backend/src/services/party*.py backend/src/models_party.py
git commit -m "test(party): 完成党建CRUD功能TDD完善，所有测试通过"
```

---

## 验收标准

完成本计划后，应满足：

✅ 所有党建模块集成测试通过（pytest全部PASS）
✅ 列表查询功能正常（分页、筛选、搜索）
✅ 数据创建验证正确（必填字段、格式验证）
✅ 数据更新符合预期（部分更新、数据一致性）
✅ 数据删除功能正常
✅ 数据库表结构匹配ORM模型
✅ 代码已提交到git
