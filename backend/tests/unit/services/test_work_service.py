# -*- coding: utf-8 -*-
"""WorkService 单元测试"""
import pytest
from unittest.mock import MagicMock, Mock, patch, call
from datetime import datetime
from sqlalchemy import asc

from src.services.work_service import WorkService
from src.models import (
    WorkCategoryResponse, WorkCategoryGroup, WorkListItem, WorkDetail,
    AdminWorkListResponse, AdminWorkListItem,
    AdminWorkCategoryListResponse, AdminWorkCategoryListItem,
    UpdateWorkRequest, UpdateWorkCategoryRequest, CreateWorkCategoryRequest
)


# ==================== Fixtures ====================

@pytest.fixture
def sample_category():
    """示例分类数据"""
    category = MagicMock()
    category.id = "category-1"
    category.name = "示例分类"
    category.icon = "academic-cap"
    category.order = 1
    category.created_at = datetime.now()
    category.updated_at = datetime.now()
    return category


@pytest.fixture
def sample_work(sample_category):
    """示例作品数据"""
    work = MagicMock()
    work.id = "work-1"
    work.name = "示例作品"
    work.description = "这是一个示例作品"
    work.category_id = "category-1"
    work.icon = "document"
    work.html_path = "works/example.html"
    work.order = 1
    work.visible = True
    work.created_at = datetime.now()
    work.updated_at = datetime.now()
    return work


@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    db = MagicMock()
    db.query.return_value = db
    db.filter.return_value = db
    db.order_by.return_value = db
    db.all.return_value = []
    db.first.return_value = None
    db.count.return_value = 0
    db.offset.return_value = db
    db.limit.return_value = db
    db.close = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.delete = MagicMock()
    return db


# ==================== 前台API测试 ====================

class TestGetCategoriesWithWorks:
    """测试获取分类及作品列表"""

    @patch('src.services.work_service.SessionLocal')
    def test_get_categories_with_works_success(self, mock_session_local, mock_db, sample_category, sample_work):
        """测试成功获取分类及作品列表"""
        mock_db.query.return_value.order_by.return_value.all.side_effect = [
            [sample_category],  # 查询分类
            [sample_work]       # 查询作品
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_categories_with_works()

        assert isinstance(result, WorkCategoryResponse)
        assert len(result.categories) == 1
        assert result.categories[0].id == "category-1"
        assert result.categories[0].name == "示例分类"
        assert len(result.categories[0].works) == 1
        assert result.categories[0].works[0].id == "work-1"

    @patch('src.services.work_service.SessionLocal')
    def test_get_categories_with_works_empty_categories(self, mock_session_local, mock_db):
        """测试空分类列表"""
        mock_db.query.return_value.order_by.return_value.all.return_value = []
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_categories_with_works()

        assert isinstance(result, WorkCategoryResponse)
        assert len(result.categories) == 0

    @patch('src.services.work_service.SessionLocal')
    def test_get_categories_with_works_skip_category_without_visible_works(self, mock_session_local, mock_db, sample_category):
        """测试跳过没有可见作品的分类"""
        mock_db.query.return_value.order_by.return_value.all.side_effect = [
            [sample_category],  # 有分类
            []                  # 但没有可见作品
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_categories_with_works()

        assert len(result.categories) == 0


class TestGetWorkDetail:
    """测试获取作品详情"""

    @patch('src.services.work_service.SessionLocal')
    def test_get_work_detail_success(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试成功获取作品详情"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,      # 查询作品
            sample_category   # 查询分类
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_work_detail("work-1")

        assert isinstance(result, WorkDetail)
        assert result.id == "work-1"
        assert result.name == "示例作品"
        assert result.category_id == "category-1"
        assert result.html_url == "/static/works/example.html"

    @patch('src.services.work_service.SessionLocal')
    def test_get_work_detail_not_found(self, mock_session_local, mock_db):
        """测试作品不存在"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_work_detail("nonexistent")

        assert result is None


# ==================== 后台管理 - 作品管理测试 ====================

class TestGetAllWorksAdmin:
    """测试获取所有作品列表（管理后台）"""

    @patch('src.services.work_service.SessionLocal')
    def test_get_all_works_admin_success(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试成功获取作品列表"""
        mock_db.count.return_value = 1
        mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_work]
        mock_db.query.return_value.filter.return_value.first.return_value = sample_category
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_all_works_admin(page=1, page_size=20)

        assert isinstance(result, AdminWorkListResponse)
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 20
        assert len(result.works) == 1
        assert result.works[0].id == "work-1"

    @patch('src.services.work_service.SessionLocal')
    def test_get_all_works_admin_with_category_filter(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试按分类筛选"""
        mock_db.count.return_value = 1
        mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_work]
        mock_db.query.return_value.filter.return_value.first.return_value = sample_category
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_all_works_admin(page=1, page_size=20, category_id="category-1")

        assert result.total == 1

    @patch('src.services.work_service.SessionLocal')
    def test_get_all_works_admin_with_visible_filter(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试按可见性筛选"""
        mock_db.count.return_value = 1
        mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_work]
        mock_db.query.return_value.filter.return_value.first.return_value = sample_category
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_all_works_admin(page=1, page_size=20, visible=True)

        assert result.total == 1

    @patch('src.services.work_service.SessionLocal')
    def test_get_all_works_admin_page_size_limit(self, mock_session_local, mock_db):
        """测试页面上限限制"""
        mock_db.count.return_value = 0
        mock_db.query.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_all_works_admin(page=1, page_size=200)

        assert result.page_size == 100  # 应该被限制到100


class TestCreateWork:
    """测试创建作品"""

    @patch('src.services.work_service.SessionLocal')
    def test_create_work_success(self, mock_session_local, mock_db, sample_category):
        """测试成功创建作品"""
        mock_db.query.return_value.first.return_value = sample_category
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.create_work(
            name="新作品",
            description="作品描述",
            category_id="category-1",
            html_path="works/new.html",
            icon="document",
            order=1,
            visible=True
        )

        assert isinstance(result, AdminWorkListItem)
        assert result.name == "新作品"
        assert result.description == "作品描述"
        assert result.category_id == "category-1"
        assert result.visible is True
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_create_work_category_not_found(self, mock_session_local, mock_db):
        """测试分类不存在"""
        mock_db.query.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = WorkService()

        with pytest.raises(ValueError, match="分类不存在"):
            service.create_work(
                name="新作品",
                description="作品描述",
                category_id="nonexistent",
                html_path="works/new.html"
            )


class TestUpdateWork:
    """测试更新作品"""

    @patch('src.services.work_service.SessionLocal')
    def test_update_work_success(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试成功更新作品"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,
            sample_category
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        request = UpdateWorkRequest(
            name="更新后的名称",
            description="更新后的描述",
            icon="new-icon",
            order=2,
            visible=False
        )

        result = service.update_work("work-1", request)

        assert isinstance(result, AdminWorkListItem)
        assert sample_work.name == "更新后的名称"
        assert sample_work.description == "更新后的描述"
        assert sample_work.visible is False
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_update_work_change_category(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试更改作品分类"""
        new_category = MagicMock()
        new_category.id = "category-2"
        new_category.name = "新分类"

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,
            new_category,
            sample_category
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        request = UpdateWorkRequest(category_id="category-2")

        result = service.update_work("work-1", request)

        assert sample_work.category_id == "category-2"

    @patch('src.services.work_service.SessionLocal')
    def test_update_work_not_found(self, mock_session_local, mock_db):
        """测试作品不存在"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = WorkService()
        request = UpdateWorkRequest(name="新名称")

        with pytest.raises(ValueError, match="作品不存在"):
            service.update_work("nonexistent", request)

    @patch('src.services.work_service.SessionLocal')
    def test_update_work_category_not_exist(self, mock_session_local, mock_db, sample_work):
        """测试更新的分类不存在"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,
            None
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        request = UpdateWorkRequest(category_id="nonexistent")

        with pytest.raises(ValueError, match="分类不存在"):
            service.update_work("work-1", request)


class TestDeleteWork:
    """测试删除作品"""

    @patch('src.services.work_service.SessionLocal')
    def test_delete_work_success(self, mock_session_local, mock_db, sample_work):
        """测试成功删除作品"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_work
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.delete_work("work-1")

        assert result == "works/example.html"
        mock_db.delete.assert_called_once_with(sample_work)
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_delete_work_not_found(self, mock_session_local, mock_db):
        """测试删除不存在的作品"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = WorkService()

        with pytest.raises(ValueError, match="作品不存在"):
            service.delete_work("nonexistent")


class TestMoveWorkUp:
    """测试上移作品"""

    @patch('src.services.work_service.SessionLocal')
    def test_move_work_up_success(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试成功上移作品"""
        prev_work = MagicMock()
        prev_work.order = 0
        sample_work.order = 1

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,
            prev_work,
            sample_category
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.move_work_up("work-1")

        assert isinstance(result, AdminWorkListItem)
        assert sample_work.order == 0
        assert prev_work.order == 1
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_move_work_up_already_first(self, mock_session_local, mock_db, sample_work):
        """测试已经是第一个作品"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,
            None  # 没有前一个作品
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()

        with pytest.raises(ValueError, match="已经是第一个作品"):
            service.move_work_up("work-1")


class TestMoveWorkDown:
    """测试下移作品"""

    @patch('src.services.work_service.SessionLocal')
    def test_move_work_down_success(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试成功下移作品"""
        next_work = MagicMock()
        next_work.order = 2
        sample_work.order = 1

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,
            next_work,
            sample_category
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.move_work_down("work-1")

        assert isinstance(result, AdminWorkListItem)
        assert sample_work.order == 2
        assert next_work.order == 1
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_move_work_down_already_last(self, mock_session_local, mock_db, sample_work):
        """测试已经是最后一个作品"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,
            None  # 没有下一个作品
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()

        with pytest.raises(ValueError, match="已经是最后一个作品"):
            service.move_work_down("work-1")


class TestToggleWorkVisibility:
    """测试切换作品可见性"""

    @patch('src.services.work_service.SessionLocal')
    def test_toggle_work_visibility_to_hidden(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试切换为隐藏"""
        sample_work.visible = True

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,
            sample_category
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        result, message = service.toggle_work_visibility("work-1")

        assert isinstance(result, AdminWorkListItem)
        assert result.visible is False
        assert message == "作品已隐藏"
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_toggle_work_visibility_to_visible(self, mock_session_local, mock_db, sample_work, sample_category):
        """测试切换为可见"""
        sample_work.visible = False

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_work,
            sample_category
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        result, message = service.toggle_work_visibility("work-1")

        assert isinstance(result, AdminWorkListItem)
        assert result.visible is True
        assert message == "作品已显示"


# ==================== 后台管理 - 分类管理测试 ====================

class TestGetAllCategoriesAdmin:
    """测试获取所有分类列表（管理后台）"""

    @patch('src.services.work_service.SessionLocal')
    def test_get_all_categories_admin_success(self, mock_session_local, mock_db, sample_category):
        """测试成功获取分类列表"""
        mock_db.query.return_value.order_by.return_value.all.return_value = [sample_category]
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.get_all_categories_admin()

        assert isinstance(result, AdminWorkCategoryListResponse)
        assert len(result.categories) == 1
        assert result.categories[0].id == "category-1"
        assert result.categories[0].work_count == 5


class TestCreateCategory:
    """测试创建分类"""

    @patch('src.services.work_service.SessionLocal')
    def test_create_category_success(self, mock_session_local, mock_db):
        """测试成功创建分类"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = WorkService()
        request = CreateWorkCategoryRequest(
            name="新分类",
            icon="folder",
            order=1
        )

        result = service.create_category(request)

        assert isinstance(result, AdminWorkCategoryListItem)
        assert result.name == "新分类"
        assert result.icon == "folder"
        assert result.order == 1
        assert result.work_count == 0
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_create_category_duplicate_name(self, mock_session_local, mock_db, sample_category):
        """测试分类名称重复"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_category
        mock_session_local.return_value = mock_db

        service = WorkService()
        request = CreateWorkCategoryRequest(
            name="示例分类",
            icon="folder",
            order=1
        )

        with pytest.raises(ValueError, match="分类名称已存在"):
            service.create_category(request)


class TestUpdateCategory:
    """测试更新分类"""

    @patch('src.services.work_service.SessionLocal')
    def test_update_category_success(self, mock_session_local, mock_db, sample_category):
        """测试成功更新分类"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_category,
            None  # 名称不重复
        ]
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_session_local.return_value = mock_db

        service = WorkService()
        request = UpdateWorkCategoryRequest(
            name="更新后的分类",
            icon="new-icon",
            order=2
        )

        result = service.update_category("category-1", request)

        assert isinstance(result, AdminWorkCategoryListItem)
        assert sample_category.name == "更新后的分类"
        assert sample_category.icon == "new-icon"
        assert sample_category.order == 2
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_update_category_name_duplicate(self, mock_session_local, mock_db, sample_category):
        """测试更新分类名称重复"""
        existing_category = MagicMock()
        existing_category.id = "other-category"

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_category,
            existing_category
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()
        request = UpdateWorkCategoryRequest(name="已存在的名称")

        with pytest.raises(ValueError, match="分类名称已被使用"):
            service.update_category("category-1", request)

    @patch('src.services.work_service.SessionLocal')
    def test_update_category_not_found(self, mock_session_local, mock_db):
        """测试分类不存在"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_session_local.return_value = mock_db

        service = WorkService()
        request = UpdateWorkCategoryRequest(name="新名称")

        with pytest.raises(ValueError, match="分类不存在"):
            service.update_category("nonexistent", request)


class TestDeleteCategory:
    """测试删除分类"""

    @patch('src.services.work_service.SessionLocal')
    def test_delete_category_success(self, mock_session_local, mock_db, sample_category):
        """测试成功删除分类"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_category
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_session_local.return_value = mock_db

        service = WorkService()
        service.delete_category("category-1")

        mock_db.delete.assert_called_once_with(sample_category)
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_delete_category_with_works(self, mock_session_local, mock_db, sample_category):
        """测试删除有作品的分类"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_category
        mock_db.query.return_value.filter.return_value.count.return_value = 5
        mock_session_local.return_value = mock_db

        service = WorkService()

        with pytest.raises(ValueError, match="分类下还有5个作品"):
            service.delete_category("category-1")


class TestMoveCategoryUp:
    """测试上移分类"""

    @patch('src.services.work_service.SessionLocal')
    def test_move_category_up_success(self, mock_session_local, mock_db, sample_category):
        """测试成功上移分类"""
        prev_category = MagicMock()
        prev_category.order = 0
        sample_category.order = 1

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_category,
            prev_category
        ]
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.move_category_up("category-1")

        assert isinstance(result, AdminWorkCategoryListItem)
        assert sample_category.order == 0
        assert prev_category.order == 1
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_move_category_up_already_first(self, mock_session_local, mock_db, sample_category):
        """测试已经是第一个分类"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_category,
            None
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()

        with pytest.raises(ValueError, match="已经是第一个分类"):
            service.move_category_up("category-1")


class TestMoveCategoryDown:
    """测试下移分类"""

    @patch('src.services.work_service.SessionLocal')
    def test_move_category_down_success(self, mock_session_local, mock_db, sample_category):
        """测试成功下移分类"""
        next_category = MagicMock()
        next_category.order = 2
        sample_category.order = 1

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_category,
            next_category
        ]
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        mock_session_local.return_value = mock_db

        service = WorkService()
        result = service.move_category_down("category-1")

        assert isinstance(result, AdminWorkCategoryListItem)
        assert sample_category.order == 2
        assert next_category.order == 1
        mock_db.commit.assert_called_once()

    @patch('src.services.work_service.SessionLocal')
    def test_move_category_down_already_last(self, mock_session_local, mock_db, sample_category):
        """测试已经是最后一个分类"""
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_category,
            None
        ]
        mock_session_local.return_value = mock_db

        service = WorkService()

        with pytest.raises(ValueError, match="已经是最后一个分类"):
            service.move_category_down("category-1")
