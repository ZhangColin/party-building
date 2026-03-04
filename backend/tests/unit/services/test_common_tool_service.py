# -*- coding: utf-8 -*-
"""CommonToolService 单元测试"""
import pytest
from unittest.mock import MagicMock, Mock, patch
from datetime import datetime
from sqlalchemy.orm import Session

from src.services.common_tool_service import CommonToolService
from src.db_models import ToolCategoryModel, CommonToolModel, CommonToolType
from src.models import (
    CommonToolCategoryResponse, ToolCategoryGroup, CommonToolListItem,
    CommonToolDetail, AdminCommonToolListResponse, AdminCommonToolListItem,
    AdminToolCategoryListResponse, AdminToolCategoryListItem,
    CreateBuiltInToolRequest, UpdateToolRequest,
    CreateToolCategoryRequest, UpdateToolCategoryRequest
)


class TestCommonToolService:
    """CommonToolService 测试类"""

    def test_init(self):
        """测试服务初始化"""
        service = CommonToolService()
        assert service is not None

    # ==================== 前端查询方法测试 ====================

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_categories_with_tools_success(self, mock_session_local):
        """测试成功获取分类及工具列表"""
        # 创建 mock 数据库会话
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的分类模型
        mock_category1 = ToolCategoryModel(
            id="cat1",
            name="教学设计",
            icon="academic-cap",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_category2 = ToolCategoryModel(
            id="cat2",
            name="资源管理",
            icon="folder",
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 创建真实的工具模型
        mock_tool1 = CommonToolModel(
            id="tool1",
            name="教案生成器",
            description="快速生成教案",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="document",
            order=1,
            visible=True,
            created_at=datetime.now()
        )

        mock_tool2 = CommonToolModel(
            id="tool2",
            name="课件预览",
            description="预览课件",
            category_id="cat1",
            type=CommonToolType.html,
            icon="eye",
            order=2,
            visible=True,
            created_at=datetime.now()
        )

        # 设置查询返回值 - 第一次返回分类列表
        mock_category_query = MagicMock()
        mock_category_query.order_by.return_value.all.return_value = [
            mock_category1, mock_category2
        ]

        # 设置工具查询的 mock 链
        # 第一次查询工具（第一个分类）返回2个工具
        mock_tool_query1 = MagicMock()
        mock_tool_query1.filter.return_value.order_by.return_value.all.return_value = [mock_tool1, mock_tool2]

        # 第二次查询工具（第二个分类）返回空列表
        mock_tool_query2 = MagicMock()
        mock_tool_query2.filter.return_value.order_by.return_value.all.return_value = []

        # 按顺序返回不同的查询
        call_count = [0]
        def query_side_effect(model):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_category_query
            elif call_count[0] == 2:
                # 第一个分类的工具查询
                return mock_tool_query1
            else:
                # 第二个分类的工具查询
                return mock_tool_query2

        mock_db.query.side_effect = query_side_effect

        # 执行测试
        service = CommonToolService()
        result = service.get_categories_with_tools()

        # 验证结果
        assert isinstance(result, CommonToolCategoryResponse)
        assert len(result.categories) == 1  # 只返回有工具的分类
        assert result.categories[0].id == "cat1"
        assert result.categories[0].name == "教学设计"
        assert len(result.categories[0].tools) == 2
        assert result.categories[0].tools[0].name == "教案生成器"

        # 验证数据库会话被正确关闭
        mock_db.close.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_categories_with_tools_empty(self, mock_session_local):
        """测试获取分类列表（空数据）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 返回空列表
        mock_db.query.return_value.order_by.return_value.all.return_value = []

        service = CommonToolService()
        result = service.get_categories_with_tools()

        assert isinstance(result, CommonToolCategoryResponse)
        assert len(result.categories) == 0

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_tool_detail_success(self, mock_session_local):
        """测试成功获取工具详情"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的工具模型实例
        mock_tool = CommonToolModel(
            id="tool1",
            name="教案生成器",
            description="快速生成教案",
            category_id="cat1",
            type=CommonToolType.html,
            icon="document",
            order=1,
            html_path="tools/lesson-generator.html",
            visible=True,
            created_at=datetime.now()
        )

        # 创建 mock 分类
        mock_category = Mock()
        mock_category.name = "教学设计"

        # 设置查询返回值 - 第一次返回工具，第二次返回分类
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.first.return_value = mock_tool

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.first.return_value = mock_category

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CommonToolService()
        result = service.get_tool_detail("tool1")

        assert isinstance(result, CommonToolDetail)
        assert result.id == "tool1"
        assert result.name == "教案生成器"
        assert result.category_name == "教学设计"
        assert result.type == "html"
        assert result.html_url == "/static/tools/lesson-generator.html"

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_tool_detail_not_found(self, mock_session_local):
        """测试获取不存在的工具详情"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 工具不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CommonToolService()
        result = service.get_tool_detail("nonexistent")

        assert result is None

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_tool_detail_built_in_tool(self, mock_session_local):
        """测试获取内置工具详情（无html_url）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的工具模型实例（内置类型）
        mock_tool = CommonToolModel(
            id="tool1",
            name="计算器",
            description="简单计算器",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="calculator",
            order=1,
            html_path=None,
            visible=True,
            created_at=datetime.now()
        )

        mock_category = Mock()
        mock_category.name = "实用工具"

        mock_query1 = MagicMock()
        mock_query1.filter.return_value.first.return_value = mock_tool

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.first.return_value = mock_category

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CommonToolService()
        result = service.get_tool_detail("tool1")

        assert isinstance(result, CommonToolDetail)
        assert result.type == "built_in"
        assert result.html_url is None

    # ==================== 后台管理方法测试（工具） ====================

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_all_tools_admin_basic(self, mock_session_local):
        """测试获取所有工具列表（基本查询）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的工具模型实例
        now = datetime.now()
        mock_tool = CommonToolModel(
            id="tool1",
            name="教案生成器",
            description="快速生成教案",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="document",
            html_path=None,
            order=1,
            visible=True,
            created_at=now,
            updated_at=now
        )

        mock_category = Mock()
        mock_category.name = "教学设计"

        # 设置查询返回值 - 需要多次调用
        mock_query = MagicMock()

        # count() 调用
        mock_query.count.return_value = 1

        # all() 调用 - 返回工具列表
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_tool]

        # first() 调用 - 返回分类
        mock_query.filter.return_value.first.return_value = mock_category

        mock_db.query.return_value = mock_query

        service = CommonToolService()
        result = service.get_all_tools_admin(page=1, page_size=20)

        assert isinstance(result, AdminCommonToolListResponse)
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 20
        assert len(result.tools) == 1
        assert result.tools[0].name == "教案生成器"

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_all_tools_admin_with_filters(self, mock_session_local):
        """测试获取所有工具列表（带筛选条件）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_tool = Mock()
        mock_tool.id = "tool1"
        mock_tool.name = "教案生成器"
        mock_tool.description = "快速生成教案"
        mock_tool.category_id = "cat1"
        mock_tool.type = CommonToolType.html
        mock_tool.icon = "document"
        mock_tool.html_path = "test.html"
        mock_tool.order = 1
        mock_tool.visible = True
        mock_tool.created_at = datetime.now()
        mock_tool.updated_at = datetime.now()

        mock_category = Mock()
        mock_category.name = "教学设计"

        mock_db.query.return_value.filter.return_value.count.return_value = 1
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_tool]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_category

        service = CommonToolService()
        result = service.get_all_tools_admin(
            page=1,
            page_size=10,
            category_id="cat1",
            tool_type="html",
            visible=True
        )

        assert isinstance(result, AdminCommonToolListResponse)
        assert result.total == 1

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_all_tools_admin_page_size_limit(self, mock_session_local):
        """测试 page_size 最大限制"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        service = CommonToolService()
        result = service.get_all_tools_admin(page=1, page_size=200)

        # 验证 page_size 被限制为最大 100
        assert result.page_size == 100

    @patch('src.services.common_tool_service.SessionLocal')
    def test_create_built_in_tool_success(self, mock_session_local):
        """测试成功创建内置工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # Mock 分类存在
        mock_category = Mock()
        mock_category.id = "cat1"
        mock_category.name = "教学设计"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_category

        # 创建请求
        request = CreateBuiltInToolRequest(
            name="新工具",
            description="工具描述",
            category_id="cat1",
            icon="star",
            order=1,
            visible=True
        )

        service = CommonToolService()
        result = service.create_built_in_tool(request)

        assert isinstance(result, AdminCommonToolListItem)
        assert result.name == "新工具"
        assert result.category_name == "教学设计"
        assert result.type == "built_in"
        assert result.html_path is None

        # 验证数据库操作
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_create_built_in_tool_category_not_found(self, mock_session_local):
        """测试创建工具时分类不存在"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 分类不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        request = CreateBuiltInToolRequest(
            name="新工具",
            description="工具描述",
            category_id="nonexistent",
            icon="star",
            order=1,
            visible=True
        )

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类不存在"):
            service.create_built_in_tool(request)

    @patch('src.services.common_tool_service.SessionLocal')
    def test_create_html_tool_success(self, mock_session_local):
        """测试成功创建HTML工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_category = Mock()
        mock_category.id = "cat1"
        mock_category.name = "教学设计"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_category

        service = CommonToolService()
        result = service.create_html_tool(
            name="HTML工具",
            description="HTML工具描述",
            category_id="cat1",
            html_path="tools/html-tool.html",
            icon="code",
            order=2,
            visible=True
        )

        assert isinstance(result, AdminCommonToolListItem)
        assert result.name == "HTML工具"
        assert result.type == "html"
        assert result.html_path == "tools/html-tool.html"

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_update_tool_success(self, mock_session_local):
        """测试成功更新工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的工具模型实例
        now = datetime.now()
        mock_tool = CommonToolModel(
            id="tool1",
            name="旧名称",
            description="旧描述",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="old-icon",
            html_path=None,
            order=1,
            visible=True,
            created_at=now,
            updated_at=now
        )

        mock_category = Mock()
        mock_category.name = "教学设计"

        # 第一次查询返回工具，第二次返回分类
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = [mock_tool, mock_category]

        mock_db.query.return_value = mock_query

        request = UpdateToolRequest(
            name="新名称",
            description="新描述",
            icon="new-icon",
            order=2,
            visible=False
        )

        service = CommonToolService()
        result = service.update_tool("tool1", request)

        assert isinstance(result, AdminCommonToolListItem)
        assert result.name == "新名称"
        assert result.description == "新描述"
        assert result.icon == "new-icon"
        assert result.order == 2
        assert result.visible is False

        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_update_tool_not_found(self, mock_session_local):
        """测试更新不存在的工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        request = UpdateToolRequest(name="新名称")

        service = CommonToolService()
        with pytest.raises(ValueError, match="工具不存在"):
            service.update_tool("nonexistent", request)

    @patch('src.services.common_tool_service.SessionLocal')
    def test_update_tool_change_category(self, mock_session_local):
        """测试更新工具的分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_tool = Mock()
        mock_tool.id = "tool1"
        mock_tool.name = "工具"
        mock_tool.description = "描述"
        mock_tool.category_id = "cat1"
        mock_tool.type = CommonToolType.built_in
        mock_tool.icon = "icon"
        mock_tool.html_path = None
        mock_tool.order = 1
        mock_tool.visible = True
        mock_tool.created_at = datetime.now()
        mock_tool.updated_at = datetime.now()

        mock_old_category = Mock()
        mock_old_category.name = "旧分类"

        mock_new_category = Mock()
        mock_new_category.id = "cat2"
        mock_new_category.name = "新分类"

        # 第一次调用返回工具，第二次返回旧分类
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_tool, mock_old_category, mock_new_category
        ]

        request = UpdateToolRequest(category_id="cat2")

        service = CommonToolService()
        result = service.update_tool("tool1", request)

        assert result.category_id == "cat2"
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_update_tool_change_category_not_found(self, mock_session_local):
        """测试更新工具时目标分类不存在"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_tool = Mock()
        mock_tool.id = "tool1"
        mock_tool.name = "工具"
        mock_tool.description = "描述"
        mock_tool.category_id = "cat1"
        mock_tool.type = CommonToolType.built_in
        mock_tool.icon = "icon"
        mock_tool.html_path = None
        mock_tool.order = 1
        mock_tool.visible = True
        mock_tool.created_at = datetime.now()
        mock_tool.updated_at = datetime.now()

        # 工具存在，但新分类不存在
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_tool, None
        ]

        request = UpdateToolRequest(category_id="nonexistent")

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类不存在"):
            service.update_tool("tool1", request)

    @patch('src.services.common_tool_service.SessionLocal')
    def test_delete_tool_success(self, mock_session_local):
        """测试成功删除工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_tool = Mock()
        mock_tool.id = "tool1"
        mock_tool.type = CommonToolType.html
        mock_tool.html_path = "tools/test.html"

        mock_db.query.return_value.filter.return_value.first.return_value = mock_tool

        service = CommonToolService()
        result = service.delete_tool("tool1")

        assert result == "tools/test.html"
        mock_db.delete.assert_called_once_with(mock_tool)
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_delete_tool_built_in(self, mock_session_local):
        """测试删除内置工具（无html_path）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_tool = Mock()
        mock_tool.id = "tool1"
        mock_tool.type = CommonToolType.built_in
        mock_tool.html_path = None

        mock_db.query.return_value.filter.return_value.first.return_value = mock_tool

        service = CommonToolService()
        result = service.delete_tool("tool1")

        assert result is None
        mock_db.delete.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_delete_tool_not_found(self, mock_session_local):
        """测试删除不存在的工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="工具不存在"):
            service.delete_tool("nonexistent")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_tool_up_success(self, mock_session_local):
        """测试成功上移工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的工具模型实例
        now = datetime.now()
        mock_tool = CommonToolModel(
            id="tool1",
            name="当前工具",
            description="描述",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="icon",
            html_path=None,
            order=2,
            visible=True,
            created_at=now,
            updated_at=now
        )

        mock_prev_tool = CommonToolModel(
            id="tool2",
            name="上一个工具",
            description="描述",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="icon",
            html_path=None,
            order=1,
            visible=True,
            created_at=now,
            updated_at=now
        )

        mock_category = Mock()
        mock_category.name = "教学设计"

        # 第一次返回当前工具，第二次返回上一个工具，第三次返回分类
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = [
            mock_tool, mock_prev_tool, mock_category
        ]
        mock_query.filter.return_value.order_by.return_value.first.return_value = mock_prev_tool

        mock_db.query.return_value = mock_query

        service = CommonToolService()
        result = service.move_tool_up("tool1")

        # 验证 order 值被交换
        assert mock_tool.order == 1
        assert mock_prev_tool.order == 2
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_tool_up_already_first(self, mock_session_local):
        """测试上移工具（已是第一个）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_tool = Mock()
        mock_tool.id = "tool1"
        mock_tool.category_id = "cat1"
        mock_tool.order = 1

        mock_db.query.return_value.filter.return_value.first.return_value = mock_tool
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="已经是第一个工具"):
            service.move_tool_up("tool1")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_tool_down_success(self, mock_session_local):
        """测试成功下移工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的工具模型实例
        now = datetime.now()
        mock_tool = CommonToolModel(
            id="tool1",
            name="当前工具",
            description="描述",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="icon",
            html_path=None,
            order=1,
            visible=True,
            created_at=now,
            updated_at=now
        )

        mock_next_tool = CommonToolModel(
            id="tool2",
            name="下一个工具",
            description="描述",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="icon",
            html_path=None,
            order=2,
            visible=True,
            created_at=now,
            updated_at=now
        )

        mock_category = Mock()
        mock_category.name = "教学设计"

        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = [
            mock_tool, mock_next_tool, mock_category
        ]
        mock_query.filter.return_value.order_by.return_value.first.return_value = mock_next_tool

        mock_db.query.return_value = mock_query

        service = CommonToolService()
        result = service.move_tool_down("tool1")

        # 验证 order 值被交换
        assert mock_tool.order == 2
        assert mock_next_tool.order == 1
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_tool_down_already_last(self, mock_session_local):
        """测试下移工具（已是最后一个）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_tool = Mock()
        mock_tool.id = "tool1"
        mock_tool.category_id = "cat1"
        mock_tool.order = 10

        mock_db.query.return_value.filter.return_value.first.return_value = mock_tool
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="已经是最后一个工具"):
            service.move_tool_down("tool1")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_toggle_tool_visibility_to_hidden(self, mock_session_local):
        """测试切换工具可见性（显示→隐藏）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的工具模型实例
        now = datetime.now()
        mock_tool = CommonToolModel(
            id="tool1",
            name="工具",
            description="描述",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="icon",
            html_path=None,
            order=1,
            visible=True,
            created_at=now,
            updated_at=now
        )

        mock_category = Mock()
        mock_category.name = "教学设计"

        # 第一次查询返回工具，第二次返回分类
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = [mock_tool, mock_category]

        mock_db.query.return_value = mock_query

        service = CommonToolService()
        result, message = service.toggle_tool_visibility("tool1")

        assert result.visible is False
        assert message == "工具已隐藏"
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_toggle_tool_visibility_to_visible(self, mock_session_local):
        """测试切换工具可见性（隐藏→显示）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的工具模型实例
        now = datetime.now()
        mock_tool = CommonToolModel(
            id="tool1",
            name="工具",
            description="描述",
            category_id="cat1",
            type=CommonToolType.built_in,
            icon="icon",
            html_path=None,
            order=1,
            visible=False,
            created_at=now,
            updated_at=now
        )

        mock_category = Mock()
        mock_category.name = "教学设计"

        # 第一次查询返回工具，第二次返回分类
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = [mock_tool, mock_category]

        mock_db.query.return_value = mock_query

        service = CommonToolService()
        result, message = service.toggle_tool_visibility("tool1")

        assert result.visible is True
        assert message == "工具已显示"
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_toggle_tool_visibility_not_found(self, mock_session_local):
        """测试切换不存在工具的可见性"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="工具不存在"):
            service.toggle_tool_visibility("nonexistent")

    # ==================== 后台管理方法测试（分类） ====================

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_all_categories_admin_success(self, mock_session_local):
        """测试成功获取所有分类列表"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的分类模型实例
        now = datetime.now()
        mock_category = ToolCategoryModel(
            id="cat1",
            name="教学设计",
            icon="academic-cap",
            order=1,
            created_at=now,
            updated_at=now
        )

        # 第一次查询：获取分类列表
        mock_category_query = MagicMock()
        mock_category_query.order_by.return_value.all.return_value = [mock_category]

        # 第二次查询：统计工具数量（在循环中调用）
        mock_tool_query = MagicMock()
        mock_tool_query.filter.return_value.count.return_value = 5

        # 按顺序返回查询对象
        mock_db.query.side_effect = [mock_category_query, mock_tool_query]

        service = CommonToolService()
        result = service.get_all_categories_admin()

        assert isinstance(result, AdminToolCategoryListResponse)
        assert len(result.categories) == 1
        assert result.categories[0].name == "教学设计"
        assert result.categories[0].tool_count == 5

    @patch('src.services.common_tool_service.SessionLocal')
    def test_create_category_success(self, mock_session_local):
        """测试成功创建分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 分类名称不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        request = CreateToolCategoryRequest(
            name="新分类",
            icon="star",
            order=1
        )

        service = CommonToolService()
        result = service.create_category(request)

        assert isinstance(result, AdminToolCategoryListItem)
        assert result.name == "新分类"
        assert result.icon == "star"
        assert result.order == 1
        assert result.tool_count == 0

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_create_category_name_exists(self, mock_session_local):
        """测试创建分类时名称已存在"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 分类名称已存在
        mock_category = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_category

        request = CreateToolCategoryRequest(
            name="已存在的分类",
            icon="star",
            order=1
        )

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类名称已存在"):
            service.create_category(request)

    @patch('src.services.common_tool_service.SessionLocal')
    def test_update_category_success(self, mock_session_local):
        """测试成功更新分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的分类模型实例
        now = datetime.now()
        mock_category = ToolCategoryModel(
            id="cat1",
            name="旧名称",
            icon="old-icon",
            order=1,
            created_at=now,
            updated_at=now
        )

        # 三次查询：
        # 1. 查询分类是否存在
        # 2. 如果更新名称，检查新名称是否已被使用
        # 3. 统计工具数量
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.first.side_effect = [mock_category, None]

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.count.return_value = 3

        mock_db.query.side_effect = [mock_query1, mock_query1, mock_query2]

        request = UpdateToolCategoryRequest(
            name="新名称",
            icon="new-icon",
            order=2
        )

        service = CommonToolService()
        result = service.update_category("cat1", request)

        assert result.name == "新名称"
        assert result.icon == "new-icon"
        assert result.order == 2
        assert result.tool_count == 3

        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_update_category_not_found(self, mock_session_local):
        """测试更新不存在的分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        request = UpdateToolCategoryRequest(name="新名称")

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类不存在"):
            service.update_category("nonexistent", request)

    @patch('src.services.common_tool_service.SessionLocal')
    def test_update_category_name_already_used(self, mock_session_local):
        """测试更新分类时名称已被使用"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_category = Mock()
        mock_category.id = "cat1"
        mock_category.name = "当前分类"

        mock_other_category = Mock()
        mock_other_category.id = "cat2"

        # 分类存在，但新名称已被其他分类使用
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_category, mock_other_category
        ]

        request = UpdateToolCategoryRequest(name="已被使用的名称")

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类名称已被使用"):
            service.update_category("cat1", request)

    @patch('src.services.common_tool_service.SessionLocal')
    def test_delete_category_success(self, mock_session_local):
        """测试成功删除分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的分类模型实例
        mock_category = ToolCategoryModel(
            id="cat1",
            name="测试分类",
            icon="icon",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 第一次查询：查询分类是否存在
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.first.return_value = mock_category

        # 第二次查询：统计工具数量（返回整数0）
        mock_query2 = MagicMock()
        mock_query2.filter.return_value.count.return_value = 0

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CommonToolService()
        service.delete_category("cat1")

        mock_db.delete.assert_called_once_with(mock_category)
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_delete_category_not_found(self, mock_session_local):
        """测试删除不存在的分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类不存在"):
            service.delete_category("nonexistent")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_delete_category_has_tools(self, mock_session_local):
        """测试删除有工具的分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建真实的分类模型实例
        mock_category = ToolCategoryModel(
            id="cat1",
            name="测试分类",
            icon="icon",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 第一次查询：查询分类是否存在
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.first.return_value = mock_category

        # 第二次查询：统计工具数量（返回整数3）
        mock_query2 = MagicMock()
        mock_query2.filter.return_value.count.return_value = 3

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类下还有3个工具"):
            service.delete_category("cat1")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_create_html_tool_category_not_found(self, mock_session_local):
        """测试创建HTML工具时分类不存在"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 分类不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类不存在"):
            service.create_html_tool(
                name="HTML工具",
                description="描述",
                category_id="nonexistent",
                html_path="test.html"
            )

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_tool_up_tool_not_found(self, mock_session_local):
        """测试上移不存在的工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="工具不存在"):
            service.move_tool_up("nonexistent")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_tool_down_tool_not_found(self, mock_session_local):
        """测试下移不存在的工具"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="工具不存在"):
            service.move_tool_down("nonexistent")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_category_up_category_not_found(self, mock_session_local):
        """测试上移不存在的分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类不存在"):
            service.move_category_up("nonexistent")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_category_down_category_not_found(self, mock_session_local):
        """测试下移不存在的分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="分类不存在"):
            service.move_category_down("nonexistent")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_category_up_success(self, mock_session_local):
        """测试成功上移分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_category = Mock()
        mock_category.id = "cat1"
        mock_category.name = "当前分类"
        mock_category.icon = "icon"
        mock_category.order = 2
        mock_category.created_at = datetime.now()
        mock_category.updated_at = datetime.now()

        mock_prev_category = Mock()
        mock_prev_category.order = 1
        mock_prev_category.updated_at = datetime.now()

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_category, mock_prev_category
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_prev_category
        mock_db.query.return_value.count.return_value = 0

        service = CommonToolService()
        result = service.move_category_up("cat1")

        # 验证 order 值被交换
        assert mock_category.order == 1
        assert mock_prev_category.order == 2
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_category_up_already_first(self, mock_session_local):
        """测试上移分类（已是第一个）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_category = Mock()
        mock_category.id = "cat1"
        mock_category.order = 1

        mock_db.query.return_value.filter.return_value.first.return_value = mock_category
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="已经是第一个分类"):
            service.move_category_up("cat1")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_category_down_success(self, mock_session_local):
        """测试成功下移分类"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_category = Mock()
        mock_category.id = "cat1"
        mock_category.name = "当前分类"
        mock_category.icon = "icon"
        mock_category.order = 1
        mock_category.created_at = datetime.now()
        mock_category.updated_at = datetime.now()

        mock_next_category = Mock()
        mock_next_category.order = 2
        mock_next_category.updated_at = datetime.now()

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_category, mock_next_category
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_next_category
        mock_db.query.return_value.count.return_value = 0

        service = CommonToolService()
        result = service.move_category_down("cat1")

        # 验证 order 值被交换
        assert mock_category.order == 2
        assert mock_next_category.order == 1
        mock_db.commit.assert_called_once()

    @patch('src.services.common_tool_service.SessionLocal')
    def test_move_category_down_already_last(self, mock_session_local):
        """测试下移分类（已是最后一个）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_category = Mock()
        mock_category.id = "cat1"
        mock_category.order = 10

        mock_db.query.return_value.filter.return_value.first.return_value = mock_category
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

        service = CommonToolService()
        with pytest.raises(ValueError, match="已经是最后一个分类"):
            service.move_category_down("cat1")

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_all_categories_admin_empty(self, mock_session_local):
        """测试获取所有分类列表（空数据）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.order_by.return_value.all.return_value = []

        service = CommonToolService()
        result = service.get_all_categories_admin()

        assert isinstance(result, AdminToolCategoryListResponse)
        assert len(result.categories) == 0

    @patch('src.services.common_tool_service.SessionLocal')
    def test_get_tool_detail_without_category(self, mock_session_local):
        """测试获取工具详情（分类不存在）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_tool = Mock()
        mock_tool.id = "tool1"
        mock_tool.name = "工具"
        mock_tool.description = "描述"
        mock_tool.category_id = "cat1"
        mock_tool.type = CommonToolType.built_in
        mock_tool.icon = "icon"
        mock_tool.order = 1
        mock_tool.html_path = None
        mock_tool.created_at = datetime.now()

        # 工具存在，但分类不存在
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_tool, None
        ]

        service = CommonToolService()
        result = service.get_tool_detail("tool1")

        assert isinstance(result, CommonToolDetail)
        assert result.category_name == "未分类"
