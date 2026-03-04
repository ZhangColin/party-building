# -*- coding: utf-8 -*-
"""测试管理员工具路由

重点测试：
- 管理员权限验证
- 工具CRUD操作
- 工具分类管理
"""
import pytest
from io import BytesIO
from pathlib import Path


@pytest.mark.asyncio
async def test_get_admin_tools_without_auth(async_client):
    """测试未认证用户访问管理工具列表"""
    response = await async_client.get("/api/v1/admin/common-tools")

    # 应该返回401未认证
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_admin_tools_non_admin(logged_in_client):
    """测试非管理员用户访问管理工具列表"""
    response = await logged_in_client.get("/api/v1/admin/common-tools")

    # 应该返回403禁止访问
    assert response.status_code == 403
    assert "需要管理员权限" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_admin_tools_success(admin_client, db_session):
    """测试管理员获取工具列表"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建测试工具
    tool = CommonToolModel(
        name="测试工具",
        description="测试描述",
        category_id=category.id,
        type="built_in",  # 使用正确的枚举值
        visible=True,
        order=1
    )
    db_session.add(tool)
    db_session.commit()

    response = await admin_client.get("/api/v1/admin/common-tools")

    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "total" in data
    assert isinstance(data["tools"], list)


@pytest.mark.asyncio
async def test_create_built_in_tool_non_admin(logged_in_client):
    """测试非管理员创建内置工具"""
    response = await logged_in_client.post(
        "/api/v1/admin/common-tools/built-in",
        json={
            "name": "测试工具",
            "description": "测试描述",
            "category_id": "test-category-id",
            "icon": "test",
            "order": 1
        }
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_built_in_tool_admin(admin_client, db_session):
    """测试管理员创建内置工具"""
    from src.db_models import ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = await admin_client.post(
        "/api/v1/admin/common-tools/built-in",
        json={
            "name": "新测试工具",
            "description": "新测试描述",
            "category_id": category.id,
            "icon": "test",
            "order": 1
        }
    )

    assert response.status_code == 201
    data = response.json()
    # 响应格式是 {"tool": {...}}
    assert "tool" in data
    assert "id" in data["tool"]


@pytest.mark.asyncio
async def test_create_built_in_tool_category_not_found(admin_client):
    """测试创建内置工具时分类不存在"""
    response = await admin_client.post(
        "/api/v1/admin/common-tools/built-in",
        json={
            "name": "新测试工具",
            "description": "新测试描述",
            "category_id": "non-existent-category-id",
            "icon": "test",
            "order": 1
        }
    )

    assert response.status_code == 404
    assert "分类不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_tool_non_admin(logged_in_client):
    """测试非管理员删除工具"""
    response = await logged_in_client.delete("/api/v1/admin/common-tools/test-tool-id")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_tool_categories_non_admin(logged_in_client):
    """测试非管理员获取工具分类"""
    response = await logged_in_client.get("/api/v1/admin/tool-categories")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_tool_categories_admin(admin_client):
    """测试管理员获取工具分类"""
    response = await admin_client.get("/api/v1/admin/tool-categories")

    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert isinstance(data["categories"], list)


@pytest.mark.asyncio
async def test_create_tool_category_non_admin(logged_in_client):
    """测试非管理员创建工具分类"""
    response = await logged_in_client.post(
        "/api/v1/admin/tool-categories",
        json={
            "name": "测试分类",
            "icon": "test",
            "order": 1
        }
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_tool_category_admin(admin_client):
    """测试管理员创建工具分类"""
    response = await admin_client.post(
        "/api/v1/admin/tool-categories",
        json={
            "name": "新分类",
            "icon": "new",
            "order": 1
        }
    )

    assert response.status_code == 201
    data = response.json()
    # 响应格式是 {"category": {...}}
    assert "category" in data
    assert "id" in data["category"]


@pytest.mark.asyncio
async def test_create_tool_category_duplicate_name(admin_client, db_session):
    """测试创建已存在名称的工具分类"""
    from src.db_models import ToolCategoryModel

    # 创建第一个分类
    category = ToolCategoryModel(
        name="重复名称",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()

    # 尝试创建同名分类
    response = await admin_client.post(
        "/api/v1/admin/tool-categories",
        json={
            "name": "重复名称",
            "icon": "another",
            "order": 2
        }
    )

    assert response.status_code == 409
    assert "已存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_move_tool_up_non_admin(logged_in_client):
    """测试非管理员移动工具"""
    response = await logged_in_client.post("/api/v1/admin/common-tools/test-tool-id/move-up")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_toggle_tool_visibility_non_admin(logged_in_client):
    """测试非管理员切换工具可见性"""
    response = await logged_in_client.post("/api/v1/admin/common-tools/test-tool-id/toggle-visibility")

    assert response.status_code == 403


# ==================== 创建HTML工具测试 ====================

@pytest.mark.asyncio
async def test_create_html_tool_non_admin(logged_in_client):
    """测试非管理员创建HTML工具"""
    html_content = b"<html><body>Test HTML</body></html>"
    files = {"html_file": ("test.html", BytesIO(html_content), "text/html")}
    data = {
        "name": "测试HTML工具",
        "description": "测试描述",
        "category_id": "test-category-id"
    }

    response = await logged_in_client.post(
        "/api/v1/admin/common-tools/html",
        data=data,
        files=files
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_html_tool_success(admin_client, db_session):
    """测试管理员创建HTML工具成功"""
    from src.db_models import ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="HTML工具分类",
        icon="html",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    html_content = b"<html><body>Test HTML Tool</body></html>"
    files = {"html_file": ("test.html", BytesIO(html_content), "text/html")}
    data = {
        "name": "测试HTML工具",
        "description": "这是一个HTML工具",
        "category_id": category.id,
        "icon": "code",
        "order": 1,
        "visible": True
    }

    response = await admin_client.post(
        "/api/v1/admin/common-tools/html",
        data=data,
        files=files
    )

    assert response.status_code == 201
    data = response.json()
    assert "tool" in data
    assert data["tool"]["name"] == "测试HTML工具"
    assert data["tool"]["type"] == "html"


@pytest.mark.asyncio
async def test_create_html_tool_invalid_file_type(admin_client, db_session):
    """测试创建HTML工具时上传非HTML文件"""
    from src.db_models import ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="HTML工具分类",
        icon="html",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 上传txt文件而非html文件
    txt_content = b"This is not HTML"
    files = {"html_file": ("test.txt", BytesIO(txt_content), "text/plain")}
    data = {
        "name": "测试工具",
        "description": "测试描述",
        "category_id": category.id
    }

    response = await admin_client.post(
        "/api/v1/admin/common-tools/html",
        data=data,
        files=files
    )

    assert response.status_code == 400
    assert "只支持.html文件" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_html_tool_file_too_large(admin_client, db_session):
    """测试创建HTML工具时文件超过5MB限制"""
    from src.db_models import ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="HTML工具分类",
        icon="html",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建超过5MB的文件
    large_content = b"<html>" + b"x" * (6 * 1024 * 1024) + b"</html>"
    files = {"html_file": ("large.html", BytesIO(large_content), "text/html")}
    data = {
        "name": "大文件工具",
        "description": "测试大文件",
        "category_id": category.id
    }

    response = await admin_client.post(
        "/api/v1/admin/common-tools/html",
        data=data,
        files=files
    )

    assert response.status_code == 400
    assert "文件大小超过5MB限制" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_html_tool_category_not_found(admin_client, db_session):
    """测试创建HTML工具时分类不存在"""
    html_content = b"<html><body>Test</body></html>"
    files = {"html_file": ("test.html", BytesIO(html_content), "text/html")}
    data = {
        "name": "测试工具",
        "description": "测试描述",
        "category_id": "non-existent-category-id"
    }

    response = await admin_client.post(
        "/api/v1/admin/common-tools/html",
        data=data,
        files=files
    )

    assert response.status_code == 404
    assert "分类不存在" in response.json()["detail"]


# ==================== 更新工具测试 ====================

@pytest.mark.asyncio
async def test_update_tool_non_admin(logged_in_client):
    """测试非管理员更新工具"""
    response = await logged_in_client.patch(
        "/api/v1/admin/common-tools/test-tool-id",
        json={"name": "更新后的名称"}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_tool_success(admin_client, db_session):
    """测试管理员更新工具成功"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建测试工具
    tool = CommonToolModel(
        name="原工具名",
        description="原描述",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    db_session.add(tool)
    db_session.commit()
    db_session.refresh(tool)

    response = await admin_client.patch(
        f"/api/v1/admin/common-tools/{tool.id}",
        json={
            "name": "更新后的工具名",
            "description": "更新后的描述"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "tool" in data
    assert data["tool"]["name"] == "更新后的工具名"
    assert data["tool"]["description"] == "更新后的描述"


@pytest.mark.asyncio
async def test_update_tool_not_found(admin_client):
    """测试更新不存在的工具"""
    response = await admin_client.patch(
        "/api/v1/admin/common-tools/non-existent-tool-id",
        json={"name": "更新后的名称"}
    )

    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


# ==================== 删除工具测试 ====================

@pytest.mark.asyncio
async def test_delete_tool_success(admin_client, db_session):
    """测试管理员删除工具成功"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建测试工具
    tool = CommonToolModel(
        name="待删除工具",
        description="测试",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    db_session.add(tool)
    db_session.commit()
    db_session.refresh(tool)

    response = await admin_client.delete(f"/api/v1/admin/common-tools/{tool.id}")

    assert response.status_code == 204

    # 验证工具已被删除
    deleted_tool = db_session.query(CommonToolModel).filter(
        CommonToolModel.id == tool.id
    ).first()
    assert deleted_tool is None


@pytest.mark.asyncio
async def test_delete_tool_not_found(admin_client):
    """测试删除不存在的工具"""
    response = await admin_client.delete("/api/v1/admin/common-tools/non-existent-tool-id")

    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_html_tool_with_files(admin_client, db_session, tmp_path):
    """测试删除HTML工具时删除相关文件"""
    from src.db_models import CommonToolModel, ToolCategoryModel
    import os

    # 创建测试分类
    category = ToolCategoryModel(
        name="HTML工具分类",
        icon="html",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建HTML工具目录和文件
    tool_id = "test123"
    # Path(__file__) = tests/integration/routers/test_admin_tools.py
    # 需要: backend/static/common_tools/html/test123
    # parent.parent.parent.parent = backend
    static_dir = Path(__file__).parent.parent.parent.parent / "static" / "common_tools" / "html" / tool_id
    static_dir.mkdir(parents=True, exist_ok=True)
    file_path = static_dir / "index.html"
    file_path.write_text("<html><body>Test</body></html>")

    # 创建测试工具
    tool = CommonToolModel(
        name="待删除HTML工具",
        description="测试",
        category_id=category.id,
        type="html",
        html_path=f"common_tools/html/{tool_id}/index.html",
        visible=True,
        order=1
    )
    db_session.add(tool)
    db_session.commit()
    db_session.refresh(tool)

    # 删除工具
    response = await admin_client.delete(f"/api/v1/admin/common-tools/{tool.id}")

    assert response.status_code == 204

    # 验证文件目录已被删除
    assert not static_dir.exists()

    # 清理：如果目录还在，手动删除
    if static_dir.exists():
        import shutil
        shutil.rmtree(static_dir, ignore_errors=True)


# ==================== 移动工具测试 ====================

@pytest.mark.asyncio
async def test_move_tool_up_success(admin_client, db_session):
    """测试上移工具成功"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建两个工具，order分别为1和2
    tool1 = CommonToolModel(
        name="工具1",
        description="描述1",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    tool2 = CommonToolModel(
        name="工具2",
        description="描述2",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=2
    )
    db_session.add_all([tool1, tool2])
    db_session.commit()
    db_session.refresh(tool2)

    # 上移工具2（order从2变为1，工具1的order变为2）
    response = await admin_client.post(f"/api/v1/admin/common-tools/{tool2.id}/move-up")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "tool" in data
    assert data["message"] == "工具已上移"


@pytest.mark.asyncio
async def test_move_tool_up_first_tool(admin_client, db_session):
    """测试上移第一个工具（应该失败）"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建第一个工具
    tool = CommonToolModel(
        name="第一个工具",
        description="描述",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    db_session.add(tool)
    db_session.commit()
    db_session.refresh(tool)

    # 尝试上移第一个工具
    response = await admin_client.post(f"/api/v1/admin/common-tools/{tool.id}/move-up")

    assert response.status_code == 400
    assert "无法上移" in response.json()["detail"]


@pytest.mark.asyncio
async def test_move_tool_up_not_found(admin_client):
    """测试上移不存在的工具"""
    response = await admin_client.post("/api/v1/admin/common-tools/non-existent-id/move-up")

    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_move_tool_down_success(admin_client, db_session):
    """测试下移工具成功"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建两个工具
    tool1 = CommonToolModel(
        name="工具1",
        description="描述1",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    tool2 = CommonToolModel(
        name="工具2",
        description="描述2",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=2
    )
    db_session.add_all([tool1, tool2])
    db_session.commit()
    db_session.refresh(tool1)

    # 下移工具1
    response = await admin_client.post(f"/api/v1/admin/common-tools/{tool1.id}/move-down")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "tool" in data
    assert data["message"] == "工具已下移"


@pytest.mark.asyncio
async def test_move_tool_down_last_tool(admin_client, db_session):
    """测试下移最后一个工具（应该失败）"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建最后一个工具
    tool = CommonToolModel(
        name="最后一个工具",
        description="描述",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    db_session.add(tool)
    db_session.commit()
    db_session.refresh(tool)

    # 尝试下移最后一个工具
    response = await admin_client.post(f"/api/v1/admin/common-tools/{tool.id}/move-down")

    assert response.status_code == 400
    assert "无法下移" in response.json()["detail"]


@pytest.mark.asyncio
async def test_move_tool_down_not_found(admin_client):
    """测试下移不存在的工具"""
    response = await admin_client.post("/api/v1/admin/common-tools/non-existent-id/move-down")

    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


# ==================== 切换工具可见性测试 ====================

@pytest.mark.asyncio
async def test_toggle_tool_visibility_success(admin_client, db_session):
    """测试切换工具可见性成功"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建可见工具
    tool = CommonToolModel(
        name="测试工具",
        description="描述",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    db_session.add(tool)
    db_session.commit()
    db_session.refresh(tool)

    # 切换可见性
    response = await admin_client.post(f"/api/v1/admin/common-tools/{tool.id}/toggle-visibility")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "tool" in data
    assert data["tool"]["visible"] == False


@pytest.mark.asyncio
async def test_toggle_tool_visibility_not_found(admin_client):
    """测试切换不存在工具的可见性"""
    response = await admin_client.post(
        "/api/v1/admin/common-tools/non-existent-id/toggle-visibility"
    )

    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


# ==================== 更新工具分类测试 ====================

@pytest.mark.asyncio
async def test_update_tool_category_non_admin(logged_in_client):
    """测试非管理员更新工具分类"""
    response = await logged_in_client.patch(
        "/api/v1/admin/tool-categories/test-category-id",
        json={"name": "更新后的名称"}
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_tool_category_success(admin_client, db_session):
    """测试管理员更新工具分类成功"""
    from src.db_models import ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="原分类名",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = await admin_client.patch(
        f"/api/v1/admin/tool-categories/{category.id}",
        json={
            "name": "更新后的分类名",
            "icon": "updated"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "category" in data
    assert data["category"]["name"] == "更新后的分类名"
    assert data["category"]["icon"] == "updated"


@pytest.mark.asyncio
async def test_update_tool_category_not_found(admin_client):
    """测试更新不存在的工具分类"""
    response = await admin_client.patch(
        "/api/v1/admin/tool-categories/non-existent-category-id",
        json={"name": "更新后的名称"}
    )

    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_tool_category_duplicate_name(admin_client, db_session):
    """测试更新工具分类为已存在的名称"""
    from src.db_models import ToolCategoryModel

    # 创建两个分类
    category1 = ToolCategoryModel(
        name="分类1",
        icon="test1",
        order=1
    )
    category2 = ToolCategoryModel(
        name="分类2",
        icon="test2",
        order=2
    )
    db_session.add_all([category1, category2])
    db_session.commit()
    db_session.refresh(category2)

    # 尝试将category2的名称更新为category1的名称
    response = await admin_client.patch(
        f"/api/v1/admin/tool-categories/{category2.id}",
        json={"name": "分类1"}
    )

    assert response.status_code == 409
    assert "已被使用" in response.json()["detail"]


# ==================== 删除工具分类测试 ====================

@pytest.mark.asyncio
async def test_delete_tool_category_non_admin(logged_in_client):
    """测试非管理员删除工具分类"""
    response = await logged_in_client.delete("/api/v1/admin/tool-categories/test-category-id")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_tool_category_success(admin_client, db_session):
    """测试管理员删除工具分类成功"""
    from src.db_models import ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="待删除分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    response = await admin_client.delete(f"/api/v1/admin/tool-categories/{category.id}")

    assert response.status_code == 204

    # 验证分类已被删除
    deleted_category = db_session.query(ToolCategoryModel).filter(
        ToolCategoryModel.id == category.id
    ).first()
    assert deleted_category is None


@pytest.mark.asyncio
async def test_delete_tool_category_not_found(admin_client):
    """测试删除不存在的工具分类"""
    response = await admin_client.delete("/api/v1/admin/tool-categories/non-existent-category-id")

    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_tool_category_with_tools(admin_client, db_session):
    """测试删除还有工具的分类"""
    from src.db_models import ToolCategoryModel, CommonToolModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="有工具的分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建工具
    tool = CommonToolModel(
        name="测试工具",
        description="描述",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    db_session.add(tool)
    db_session.commit()

    # 尝试删除还有工具的分类
    response = await admin_client.delete(f"/api/v1/admin/tool-categories/{category.id}")

    assert response.status_code == 400
    assert "还有" in response.json()["detail"] and "工具" in response.json()["detail"]


# ==================== 移动工具分类测试 ====================

@pytest.mark.asyncio
async def test_move_category_up_non_admin(logged_in_client):
    """测试非管理员上移分类"""
    response = await logged_in_client.post("/api/v1/admin/tool-categories/test-category-id/move-up")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_move_category_up_success(admin_client, db_session):
    """测试上移分类成功"""
    from src.db_models import ToolCategoryModel

    # 创建两个分类
    category1 = ToolCategoryModel(
        name="分类1",
        icon="test1",
        order=1
    )
    category2 = ToolCategoryModel(
        name="分类2",
        icon="test2",
        order=2
    )
    db_session.add_all([category1, category2])
    db_session.commit()
    db_session.refresh(category2)

    # 上移分类2
    response = await admin_client.post(f"/api/v1/admin/tool-categories/{category2.id}/move-up")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "category" in data
    assert data["message"] == "分类已上移"


@pytest.mark.asyncio
async def test_move_category_up_first_category(admin_client, db_session):
    """测试上移第一个分类（应该失败）"""
    from src.db_models import ToolCategoryModel

    # 创建第一个分类
    category = ToolCategoryModel(
        name="第一个分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 尝试上移第一个分类
    response = await admin_client.post(f"/api/v1/admin/tool-categories/{category.id}/move-up")

    assert response.status_code == 400
    assert "无法上移" in response.json()["detail"]


@pytest.mark.asyncio
async def test_move_category_up_not_found(admin_client):
    """测试上移不存在的分类"""
    response = await admin_client.post("/api/v1/admin/tool-categories/non-existent-id/move-up")

    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_move_category_down_non_admin(logged_in_client):
    """测试非管理员下移分类"""
    response = await logged_in_client.post("/api/v1/admin/tool-categories/test-category-id/move-down")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_move_category_down_success(admin_client, db_session):
    """测试下移分类成功"""
    from src.db_models import ToolCategoryModel

    # 创建两个分类
    category1 = ToolCategoryModel(
        name="分类1",
        icon="test1",
        order=1
    )
    category2 = ToolCategoryModel(
        name="分类2",
        icon="test2",
        order=2
    )
    db_session.add_all([category1, category2])
    db_session.commit()
    db_session.refresh(category1)

    # 下移分类1
    response = await admin_client.post(f"/api/v1/admin/tool-categories/{category1.id}/move-down")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "category" in data
    assert data["message"] == "分类已下移"


@pytest.mark.asyncio
async def test_move_category_down_last_category(admin_client, db_session):
    """测试下移最后一个分类（应该失败）"""
    from src.db_models import ToolCategoryModel

    # 创建最后一个分类
    category = ToolCategoryModel(
        name="最后一个分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 尝试下移最后一个分类
    response = await admin_client.post(f"/api/v1/admin/tool-categories/{category.id}/move-down")

    assert response.status_code == 400
    assert "无法下移" in response.json()["detail"]


@pytest.mark.asyncio
async def test_move_category_down_not_found(admin_client):
    """测试下移不存在的分类"""
    response = await admin_client.post("/api/v1/admin/tool-categories/non-existent-id/move-down")

    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


# ==================== 分页和筛选测试 ====================

@pytest.mark.asyncio
async def test_get_admin_tools_with_pagination(admin_client, db_session):
    """测试工具列表分页"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建25个工具
    for i in range(25):
        tool = CommonToolModel(
            name=f"工具{i}",
            description=f"描述{i}",
            category_id=category.id,
            type="built_in",
            visible=True,
            order=i
        )
        db_session.add(tool)
    db_session.commit()

    # 请求第一页（每页20个）
    response = await admin_client.get("/api/v1/admin/common-tools?page=1&page_size=20")

    assert response.status_code == 200
    data = response.json()
    assert len(data["tools"]) == 20
    assert data["total"] == 25

    # 请求第二页
    response = await admin_client.get("/api/v1/admin/common-tools?page=2&page_size=20")

    assert response.status_code == 200
    data = response.json()
    assert len(data["tools"]) == 5
    assert data["total"] == 25


@pytest.mark.asyncio
async def test_get_admin_tools_with_category_filter(admin_client, db_session):
    """测试按分类筛选工具"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建两个分类
    category1 = ToolCategoryModel(
        name="分类1",
        icon="test1",
        order=1
    )
    category2 = ToolCategoryModel(
        name="分类2",
        icon="test2",
        order=2
    )
    db_session.add_all([category1, category2])
    db_session.commit()
    db_session.refresh(category1)
    db_session.refresh(category2)

    # 为两个分类创建工具
    tool1 = CommonToolModel(
        name="工具1",
        description="描述1",
        category_id=category1.id,
        type="built_in",
        visible=True,
        order=1
    )
    tool2 = CommonToolModel(
        name="工具2",
        description="描述2",
        category_id=category2.id,
        type="built_in",
        visible=True,
        order=2
    )
    db_session.add_all([tool1, tool2])
    db_session.commit()

    # 按分类1筛选
    response = await admin_client.get(
        f"/api/v1/admin/common-tools?category_id={category1.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["tools"]) == 1
    assert data["tools"][0]["name"] == "工具1"


@pytest.mark.asyncio
async def test_get_admin_tools_with_type_filter(admin_client, db_session):
    """测试按类型筛选工具"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建不同类型的工具
    tool1 = CommonToolModel(
        name="内置工具",
        description="描述1",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    tool2 = CommonToolModel(
        name="HTML工具",
        description="描述2",
        category_id=category.id,
        type="html",
        html_path="common_tools/html/test/index.html",
        visible=True,
        order=2
    )
    db_session.add_all([tool1, tool2])
    db_session.commit()

    # 按类型筛选
    response = await admin_client.get("/api/v1/admin/common-tools?type=built_in")

    assert response.status_code == 200
    data = response.json()
    assert len(data["tools"]) == 1
    assert data["tools"][0]["type"] == "built_in"


@pytest.mark.asyncio
async def test_get_admin_tools_with_visibility_filter(admin_client, db_session):
    """测试按可见性筛选工具"""
    from src.db_models import CommonToolModel, ToolCategoryModel

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    # 创建可见和不可见的工具
    tool1 = CommonToolModel(
        name="可见工具",
        description="描述1",
        category_id=category.id,
        type="built_in",
        visible=True,
        order=1
    )
    tool2 = CommonToolModel(
        name="隐藏工具",
        description="描述2",
        category_id=category.id,
        type="built_in",
        visible=False,
        order=2
    )
    db_session.add_all([tool1, tool2])
    db_session.commit()

    # 只显示可见的工具
    response = await admin_client.get("/api/v1/admin/common-tools?visible=true")

    assert response.status_code == 200
    data = response.json()
    assert len(data["tools"]) == 1
    assert data["tools"][0]["visible"] == True


@pytest.mark.asyncio
async def test_get_admin_tools_error_handling(admin_client, db_session):
    """测试工具列表接口的错误处理"""
    from src.db_models import CommonToolModel, ToolCategoryModel
    from unittest.mock import patch

    # 创建测试分类
    category = ToolCategoryModel(
        name="测试分类",
        icon="test",
        order=1
    )
    db_session.add(category)
    db_session.commit()

    # Mock service抛出异常
    with patch('src.interfaces.routers.admin.tools.get_common_tool_service') as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.get_all_tools_admin.side_effect = Exception("数据库连接失败")

        response = await admin_client.get("/api/v1/admin/common-tools")

        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_tool_categories_error_handling(admin_client):
    """测试工具分类列表接口的错误处理"""
    from unittest.mock import patch

    # Mock service抛出异常
    with patch('src.interfaces.routers.admin.tools.get_common_tool_service') as mock_service:
        mock_instance = mock_service.return_value
        mock_instance.get_all_categories_admin.side_effect = Exception("数据库连接失败")

        response = await admin_client.get("/api/v1/admin/tool-categories")

        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]
