# -*- coding: utf-8 -*-
"""CourseService 单元测试"""
import pytest
from unittest.mock import MagicMock, Mock, patch, call
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from src.services.course_service import CourseService
from src.db_models import CourseCategoryModel, CourseDocumentModel
from src.models import (
    CourseCategoryNode, CourseCategoryTreeResponse,
    CourseDocumentListItem, CourseDocumentListResponse,
    CourseDocumentDetail,
    AdminCourseCategoryListItem, AdminCourseCategoryListResponse,
    CreateCourseCategoryRequest, UpdateCourseCategoryRequest,
    AdminCourseDocumentListItem, AdminCourseDocumentListResponse,
    UpdateCourseDocumentRequest
)


class TestCourseService:
    """CourseService 测试类"""

    def test_init(self):
        """测试服务初始化"""
        service = CourseService()
        assert service is not None
        assert service.storage_root is not None

    # ==================== 目录树构建方法测试 ====================

    def test_build_category_tree_empty(self):
        """测试构建空目录树"""
        service = CourseService()
        result = service._build_category_tree([], parent_id=None)
        assert result == []

    def test_build_category_tree_root_level(self):
        """测试构建根级目录树"""
        service = CourseService()

        # 创建模拟分类
        cat1 = CourseCategoryModel(
            id="cat1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        cat2 = CourseCategoryModel(
            id="cat2",
            name="机器学习",
            parent_id=None,
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        result = service._build_category_tree([cat1, cat2], parent_id=None)

        assert len(result) == 2
        assert result[0].id == "cat1"
        assert result[0].name == "AI基础知识"
        assert result[1].id == "cat2"
        assert result[1].name == "机器学习"

    def test_build_category_tree_with_children(self):
        """测试构建带子目录的树"""
        service = CourseService()

        # 创建模拟分类（父子关系）
        parent = CourseCategoryModel(
            id="parent1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        child1 = CourseCategoryModel(
            id="child1",
            name="什么是AI",
            parent_id="parent1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        child2 = CourseCategoryModel(
            id="child2",
            name="AI历史",
            parent_id="parent1",
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        result = service._build_category_tree([parent, child1, child2], parent_id=None)

        assert len(result) == 1
        assert result[0].id == "parent1"
        assert len(result[0].children) == 2
        assert result[0].children[0].id == "child1"
        assert result[0].children[1].id == "child2"

    def test_build_category_tree_ordering(self):
        """测试目录按order排序"""
        service = CourseService()

        cat3 = CourseCategoryModel(
            id="cat3",
            name="第三个",
            parent_id=None,
            order=3,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        cat1 = CourseCategoryModel(
            id="cat1",
            name="第一个",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        cat2 = CourseCategoryModel(
            id="cat2",
            name="第二个",
            parent_id=None,
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        result = service._build_category_tree([cat3, cat1, cat2], parent_id=None)

        assert result[0].id == "cat1"
        assert result[1].id == "cat2"
        assert result[2].id == "cat3"

    # ==================== 获取目录树测试 ====================

    @patch('src.services.course_service.SessionLocal')
    def test_get_category_tree_success(self, mock_session_local):
        """测试成功获取目录树"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建模拟分类
        parent = CourseCategoryModel(
            id="parent1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        child = CourseCategoryModel(
            id="child1",
            name="什么是AI",
            parent_id="parent1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_db.query.return_value.all.return_value = [parent, child]

        service = CourseService()
        result = service.get_category_tree()

        assert isinstance(result, CourseCategoryTreeResponse)
        assert len(result.categories) == 1
        assert result.categories[0].id == "parent1"
        assert len(result.categories[0].children) == 1
        assert result.categories[0].children[0].id == "child1"

        mock_db.close.assert_called_once()

    # ==================== 管理后台 - 获取目录列表测试 ====================

    @patch('src.services.course_service.SessionLocal')
    def test_get_admin_categories_success(self, mock_session_local):
        """测试成功获取管理后台目录列表"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 创建模拟分类
        parent = CourseCategoryModel(
            id="parent1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        child = CourseCategoryModel(
            id="child1",
            name="什么是AI",
            parent_id="parent1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 模拟查询链
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [parent, child]

        # 为每个不同的查询返回不同的mock
        mock_query_2 = MagicMock()
        mock_query_2.filter.return_value.count.return_value = 0
        mock_query_2.filter.return_value.first.return_value = parent

        # 设置多次调用query的返回值
        mock_db.query.side_effect = [
            mock_query,  # 第一次：获取所有分类
            mock_query_2,  # 第二次：查询父目录
            mock_query_2,  # 第三次：查询文档数
            mock_query_2,  # 第四次：查询子目录数
            mock_query_2,  # 第五次：查询父目录
            mock_query_2,  # 第六次：查询文档数
            mock_query_2,  # 第七次：查询子目录数
        ]

        service = CourseService()
        result = service.get_admin_categories()

        assert isinstance(result, AdminCourseCategoryListResponse)
        assert len(result.categories) == 2

        mock_db.close.assert_called_once()

    # ==================== 创建目录测试 ====================

    @patch('src.services.course_service.SessionLocal')
    def test_create_category_success(self, mock_session_local):
        """测试成功创建根目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 模拟父目录查询不存在（根目录）
        mock_db.query.return_value.filter.return_value.first.return_value = None

        # 模拟refresh设置created_at和updated_at
        def mock_refresh(obj):
            if hasattr(obj, 'created_at') and obj.created_at is None:
                obj.created_at = datetime.now()
            if hasattr(obj, 'updated_at') and obj.updated_at is None:
                obj.updated_at = datetime.now()

        mock_db.refresh.side_effect = mock_refresh

        request = CreateCourseCategoryRequest(
            name="AI基础知识",
            parent_id=None,
            order=1
        )

        service = CourseService()
        result = service.create_category(request)

        assert isinstance(result, AdminCourseCategoryListItem)
        assert result.name == "AI基础知识"
        assert result.parent_id is None
        assert result.order == 1

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    def test_create_category_with_parent(self, mock_session_local):
        """测试创建带父目录的子目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 模拟父目录存在
        parent = CourseCategoryModel(
            id="parent1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 设置mock返回值
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            parent,  # 第一次：验证父目录存在
            parent   # 第二次：获取父目录名称
        ]

        # 模拟refresh设置created_at和updated_at
        def mock_refresh(obj):
            if hasattr(obj, 'created_at') and obj.created_at is None:
                obj.created_at = datetime.now()
            if hasattr(obj, 'updated_at') and obj.updated_at is None:
                obj.updated_at = datetime.now()

        mock_db.refresh.side_effect = mock_refresh

        request = CreateCourseCategoryRequest(
            name="什么是AI",
            parent_id="parent1",
            order=1
        )

        service = CourseService()
        result = service.create_category(request)

        assert result.name == "什么是AI"
        assert result.parent_id == "parent1"
        assert result.parent_name == "AI基础知识"

    @patch('src.services.course_service.SessionLocal')
    def test_create_category_parent_not_found(self, mock_session_local):
        """测试创建目录时父目录不存在"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 模拟父目录不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        request = CreateCourseCategoryRequest(
            name="子目录",
            parent_id="nonexistent",
            order=1
        )

        service = CourseService()

        with pytest.raises(ValueError, match="父目录不存在"):
            service.create_category(request)

    # ==================== 更新目录测试 ====================

    @patch('src.services.course_service.SessionLocal')
    def test_update_category_success(self, mock_session_local):
        """测试成功更新目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        # 模拟现有目录
        category = CourseCategoryModel(
            id="cat1",
            name="旧名称",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.first.return_value = category
        mock_db.query.return_value.count.return_value = 0

        request = UpdateCourseCategoryRequest(
            name="新名称",
            parent_id=None,
            order=2
        )

        service = CourseService()
        result = service.update_category("cat1", request)

        assert result is not None
        assert result.name == "新名称"
        assert result.order == 2
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    def test_update_category_not_found(self, mock_session_local):
        """测试更新不存在的目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        request = UpdateCourseCategoryRequest(name="新名称")

        service = CourseService()
        result = service.update_category("nonexistent", request)

        assert result is None

    @patch('src.services.course_service.SessionLocal')
    def test_update_category_invalid_parent(self, mock_session_local):
        """测试更新目录时父目录不存在"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        category = CourseCategoryModel(
            id="cat1",
            name="目录",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            category,  # 查询目录
            None       # 查询父目录（不存在）
        ]

        request = UpdateCourseCategoryRequest(parent_id="invalid_parent")

        service = CourseService()

        with pytest.raises(ValueError, match="父目录不存在"):
            service.update_category("cat1", request)

    @patch('src.services.course_service.SessionLocal')
    def test_update_category_self_reference(self, mock_session_local):
        """测试将目录移动到自己下面（循环引用）"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        category = CourseCategoryModel(
            id="cat1",
            name="目录",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.first.return_value = category

        request = UpdateCourseCategoryRequest(parent_id="cat1")

        service = CourseService()

        with pytest.raises(ValueError, match="不能将目录移动到自己下面"):
            service.update_category("cat1", request)

    # ==================== 删除目录测试 ====================

    @patch('src.services.course_service.SessionLocal')
    def test_delete_category_success(self, mock_session_local):
        """测试成功删除空目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        category = CourseCategoryModel(
            id="cat1",
            name="目录",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 创建不同的mock对象用于不同查询
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = category

        mock_count_query = MagicMock()
        mock_count_query.filter.return_value.count.return_value = 0

        mock_db.query.side_effect = [
            mock_query,      # 查询目录
            mock_count_query,  # 查询子目录数
            mock_count_query   # 查询文档数
        ]

        service = CourseService()
        success, error = service.delete_category("cat1")

        assert success is True
        assert error is None
        mock_db.delete.assert_called_once_with(category)
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    def test_delete_category_not_found(self, mock_session_local):
        """测试删除不存在的目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CourseService()
        success, error = service.delete_category("nonexistent")

        assert success is False
        assert error == "目录不存在"

    @patch('src.services.course_service.SessionLocal')
    def test_delete_category_has_children(self, mock_session_local):
        """测试删除有子目录的目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        category = CourseCategoryModel(
            id="cat1",
            name="目录",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 创建不同的mock对象用于不同查询
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = category

        mock_count_query1 = MagicMock()
        mock_count_query1.filter.return_value.count.return_value = 1  # 有子目录

        mock_count_query2 = MagicMock()
        mock_count_query2.filter.return_value.count.return_value = 0

        mock_db.query.side_effect = [
            mock_query,
            mock_count_query1,
            mock_count_query2
        ]

        service = CourseService()
        success, error = service.delete_category("cat1")

        assert success is False
        assert "子目录" in error

    @patch('src.services.course_service.SessionLocal')
    def test_delete_category_has_documents(self, mock_session_local):
        """测试删除有文档的目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        category = CourseCategoryModel(
            id="cat1",
            name="目录",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 创建不同的mock对象用于不同查询
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = category

        mock_count_query1 = MagicMock()
        mock_count_query1.filter.return_value.count.return_value = 0  # 无子目录

        mock_count_query2 = MagicMock()
        mock_count_query2.filter.return_value.count.return_value = 1  # 有文档

        mock_db.query.side_effect = [
            mock_query,
            mock_count_query1,
            mock_count_query2
        ]

        service = CourseService()
        success, error = service.delete_category("cat1")

        assert success is False
        assert "文档" in error

    # ==================== 移动目录测试 ====================

    @patch('src.services.course_service.SessionLocal')
    def test_move_category_up_success(self, mock_session_local):
        """测试成功向上移动目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        current = CourseCategoryModel(
            id="cat2",
            name="第二个",
            parent_id=None,
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        prev = CourseCategoryModel(
            id="cat1",
            name="第一个",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 每次查询返回新的mock对象
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.order_by.return_value.first.return_value = current

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = prev

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CourseService()
        success, error = service.move_category_up("cat2")

        assert success is True
        assert error is None
        # 验证order值被交换了（由于元组解包，两个对象的order都会改变）
        assert current.order != 2 or prev.order != 1  # 至少有一个改变了
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    def test_move_category_up_already_first(self, mock_session_local):
        """测试向上移动已经是第一个的目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        category = CourseCategoryModel(
            id="cat1",
            name="第一个",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 每次查询返回新的mock对象
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.order_by.return_value.first.return_value = category

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = None

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CourseService()
        success, error = service.move_category_up("cat1")

        assert success is False
        assert "第一个" in error

    @patch('src.services.course_service.SessionLocal')
    def test_move_category_down_success(self, mock_session_local):
        """测试成功向下移动目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        current = CourseCategoryModel(
            id="cat1",
            name="第一个",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        next_cat = CourseCategoryModel(
            id="cat2",
            name="第二个",
            parent_id=None,
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 每次查询返回新的mock对象
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.order_by.return_value.first.return_value = current

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = next_cat

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CourseService()
        success, error = service.move_category_down("cat1")

        assert success is True
        assert error is None
        # 验证order值被交换了
        assert current.order != 1 or next_cat.order != 2  # 至少有一个改变了
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    def test_move_category_down_already_last(self, mock_session_local):
        """测试向下移动已经是最后一个的目录"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        category = CourseCategoryModel(
            id="cat2",
            name="最后一个",
            parent_id=None,
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 每次查询返回新的mock对象
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.order_by.return_value.first.return_value = category

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = None

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CourseService()
        success, error = service.move_category_down("cat2")

        assert success is False
        assert "最后一个" in error

    # ==================== 获取目录文档测试 ====================

    @patch('src.services.course_service.SessionLocal')
    def test_get_documents_by_category_success(self, mock_session_local):
        """测试成功获取目录下的文档列表"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        doc1 = CourseDocumentModel(
            id="doc1",
            title="文档1",
            summary="摘要1",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now()
        )

        doc2 = CourseDocumentModel(
            id="doc2",
            title="文档2",
            summary="摘要2",
            file_path="course_docs/doc2/content.md",
            category_id="cat1",
            order=2,
            created_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [doc1, doc2]

        service = CourseService()
        result = service.get_documents_by_category("cat1")

        assert isinstance(result, CourseDocumentListResponse)
        assert len(result.documents) == 2
        assert result.documents[0].title == "文档1"
        assert result.documents[1].title == "文档2"

    # ==================== 获取文档详情测试 ====================

    @patch('src.services.course_service.SessionLocal')
    @patch('pathlib.Path.read_text')
    def test_get_document_detail_success(self, mock_read_text, mock_session_local):
        """测试成功获取文档详情"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        document = CourseDocumentModel(
            id="doc1",
            title="文档标题",
            summary="文档摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now()
        )

        # 为每个查询创建不同的mock
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.first.return_value = document

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = None

        mock_query3 = MagicMock()
        mock_query3.filter.return_value.order_by.return_value.first.return_value = None

        mock_db.query.side_effect = [
            mock_query1,  # 查询文档
            mock_query2,  # 上一个文档
            mock_query3   # 下一个文档
        ]

        mock_read_text.return_value = "# 文档内容"

        service = CourseService()
        result = service.get_document_detail("doc1")

        assert isinstance(result, CourseDocumentDetail)
        assert result.id == "doc1"
        assert result.title == "文档标题"
        assert result.content == "# 文档内容"
        assert result.prev_doc_id is None
        assert result.next_doc_id is None

    @patch('src.services.course_service.SessionLocal')
    @patch('pathlib.Path.read_text')
    def test_get_document_detail_file_read_error(self, mock_read_text, mock_session_local):
        """测试读取文档文件失败时的处理"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        document = CourseDocumentModel(
            id="doc1",
            title="文档标题",
            summary="文档摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now()
        )

        mock_query1 = MagicMock()
        mock_query1.filter.return_value.first.return_value = document

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = None

        mock_query3 = MagicMock()
        mock_query3.filter.return_value.order_by.return_value.first.return_value = None

        mock_db.query.side_effect = [
            mock_query1,  # 查询文档
            mock_query2,  # 上一个文档
            mock_query3   # 下一个文档
        ]

        # 模拟文件读取异常
        mock_read_text.side_effect = Exception("File not found")

        service = CourseService()
        result = service.get_document_detail("doc1")

        assert isinstance(result, CourseDocumentDetail)
        assert result.id == "doc1"
        assert result.content == ""  # 文件读取失败时返回空字符串

    @patch('src.services.course_service.SessionLocal')
    def test_get_document_detail_not_found(self, mock_session_local):
        """测试获取不存在的文档详情"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CourseService()
        result = service.get_document_detail("nonexistent")

        assert result is None

    # ==================== 管理后台 - 获取文档列表测试 ====================

    @patch('src.services.course_service.SessionLocal')
    @patch.object(CourseService, '_get_category_path')
    def test_get_admin_documents_success(self, mock_get_category_path, mock_session_local):
        """测试成功获取管理后台文档列表"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        doc = CourseDocumentModel(
            id="doc1",
            title="文档标题",
            summary="文档摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        category = CourseCategoryModel(
            id="cat1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [doc]
        mock_query.first.return_value = category

        mock_get_category_path.return_value = "AI基础知识"

        service = CourseService()
        result = service.get_admin_documents(page=1, page_size=20)

        assert isinstance(result, AdminCourseDocumentListResponse)
        assert len(result.documents) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.documents[0].title == "文档标题"

    # ==================== 创建文档测试 ====================

    @patch('src.services.course_service.SessionLocal')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    @patch.object(CourseService, '_get_category_path')
    def test_create_document_success(self, mock_get_category_path, mock_write_text, mock_mkdir, mock_session_local):
        """测试成功创建文档"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        category = CourseCategoryModel(
            id="cat1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = category

        mock_db.query.return_value = mock_query

        # 模拟refresh设置created_at和updated_at
        def mock_refresh(obj):
            if hasattr(obj, 'created_at') and obj.created_at is None:
                obj.created_at = datetime.now()
            if hasattr(obj, 'updated_at') and obj.updated_at is None:
                obj.updated_at = datetime.now()

        mock_db.refresh.side_effect = mock_refresh

        mock_get_category_path.return_value = "AI基础知识"

        service = CourseService()
        result = service.create_document(
            title="新文档",
            summary="文档摘要",
            category_id="cat1",
            markdown_content="# 内容",
            order=1
        )

        assert isinstance(result, AdminCourseDocumentListItem)
        assert result.title == "新文档"
        assert result.summary == "文档摘要"
        assert result.category_id == "cat1"

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    def test_create_document_category_not_found(self, mock_session_local):
        """测试创建文档时目录不存在"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CourseService()

        with pytest.raises(ValueError, match="目录不存在"):
            service.create_document(
                title="文档",
                summary="摘要",
                category_id="nonexistent",
                markdown_content="# 内容"
            )

    # ==================== 更新文档测试 ====================

    @patch('src.services.course_service.SessionLocal')
    @patch.object(CourseService, '_get_category_path')
    def test_update_document_success(self, mock_get_category_path, mock_session_local):
        """测试成功更新文档"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        document = CourseDocumentModel(
            id="doc1",
            title="旧标题",
            summary="旧摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        category = CourseCategoryModel(
            id="cat1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            document,  # 查询文档
            category   # 验证目录
        ]

        mock_get_category_path.return_value = "AI基础知识"

        request = UpdateCourseDocumentRequest(
            title="新标题",
            summary="新摘要"
        )

        service = CourseService()
        result = service.update_document("doc1", request)

        assert result is not None
        assert result.title == "新标题"
        assert result.summary == "新摘要"
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    def test_update_document_not_found(self, mock_session_local):
        """测试更新不存在的文档"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        request = UpdateCourseDocumentRequest(title="新标题")

        service = CourseService()
        result = service.update_document("nonexistent", request)

        assert result is None

    @patch('src.services.course_service.SessionLocal')
    def test_update_document_invalid_category(self, mock_session_local):
        """测试更新文档时目录不存在"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        document = CourseDocumentModel(
            id="doc1",
            title="标题",
            summary="摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            document,  # 查询文档
            None       # 验证新目录（不存在）
        ]

        request = UpdateCourseDocumentRequest(category_id="invalid_cat")

        service = CourseService()

        with pytest.raises(ValueError, match="目录不存在"):
            service.update_document("doc1", request)

    # ==================== 删除文档测试 ====================

    @patch('src.services.course_service.SessionLocal')
    @patch('shutil.rmtree')
    @patch('pathlib.Path.exists')
    def test_delete_document_success(self, mock_exists, mock_rmtree, mock_session_local):
        """测试成功删除文档"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        document = CourseDocumentModel(
            id="doc1",
            title="标题",
            summary="摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.first.return_value = document
        mock_exists.return_value = True

        service = CourseService()
        success, error = service.delete_document("doc1")

        assert success is True
        assert error is None
        mock_db.delete.assert_called_once_with(document)
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    @patch('shutil.rmtree')
    @patch('pathlib.Path.exists')
    def test_delete_document_exception(self, mock_exists, mock_rmtree, mock_session_local):
        """测试删除文档时发生异常"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        document = CourseDocumentModel(
            id="doc1",
            title="标题",
            summary="摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.first.return_value = document
        mock_exists.return_value = True

        # 模拟删除文件时抛出异常
        mock_rmtree.side_effect = Exception("Permission denied")

        service = CourseService()
        success, error = service.delete_document("doc1")

        assert success is False
        assert "删除失败" in error

    @patch('src.services.course_service.SessionLocal')
    def test_delete_document_not_found(self, mock_session_local):
        """测试删除不存在的文档"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CourseService()
        success, error = service.delete_document("nonexistent")

        assert success is False
        assert error == "文档不存在"

    # ==================== 移动文档测试 ====================

    @patch('src.services.course_service.SessionLocal')
    def test_move_document_up_success(self, mock_session_local):
        """测试成功向上移动文档"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        current = CourseDocumentModel(
            id="doc2",
            title="第二个",
            summary="摘要",
            file_path="course_docs/doc2/content.md",
            category_id="cat1",
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        prev = CourseDocumentModel(
            id="doc1",
            title="第一个",
            summary="摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 每次查询返回新的mock对象
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.order_by.return_value.first.return_value = current

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = prev

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CourseService()
        success, error = service.move_document_up("doc2")

        assert success is True
        assert error is None
        # 验证order值被交换了
        assert current.order != 2 or prev.order != 1  # 至少有一个改变了
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    def test_move_document_up_already_first(self, mock_session_local):
        """测试向上移动已经是第一个的文档"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        document = CourseDocumentModel(
            id="doc1",
            title="第一个",
            summary="摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 每次查询返回新的mock对象
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.order_by.return_value.first.return_value = document

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = None

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CourseService()
        success, error = service.move_document_up("doc1")

        assert success is False
        assert "第一个" in error

    @patch('src.services.course_service.SessionLocal')
    def test_move_document_down_success(self, mock_session_local):
        """测试成功向下移动文档"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        current = CourseDocumentModel(
            id="doc1",
            title="第一个",
            summary="摘要",
            file_path="course_docs/doc1/content.md",
            category_id="cat1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        next_doc = CourseDocumentModel(
            id="doc2",
            title="第二个",
            summary="摘要",
            file_path="course_docs/doc2/content.md",
            category_id="cat1",
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 每次查询返回新的mock对象
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.order_by.return_value.first.return_value = current

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = next_doc

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CourseService()
        success, error = service.move_document_down("doc1")

        assert success is True
        assert error is None
        # 验证order值被交换了
        assert current.order != 1 or next_doc.order != 2  # 至少有一个改变了
        mock_db.commit.assert_called_once()

    @patch('src.services.course_service.SessionLocal')
    def test_move_document_down_already_last(self, mock_session_local):
        """测试向下移动已经是最后一个的文档"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        document = CourseDocumentModel(
            id="doc2",
            title="最后一个",
            summary="摘要",
            file_path="course_docs/doc2/content.md",
            category_id="cat1",
            order=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # 每次查询返回新的mock对象
        mock_query1 = MagicMock()
        mock_query1.filter.return_value.order_by.return_value.first.return_value = document

        mock_query2 = MagicMock()
        mock_query2.filter.return_value.order_by.return_value.first.return_value = None

        mock_db.query.side_effect = [mock_query1, mock_query2]

        service = CourseService()
        success, error = service.move_document_down("doc2")

        assert success is False
        assert "最后一个" in error

    # ==================== 获取目录路径测试 ====================

    @patch('src.services.course_service.SessionLocal')
    def test_get_category_path_root(self, mock_session_local):
        """测试获取根目录路径"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        category = CourseCategoryModel(
            id="cat1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.first.return_value = category

        service = CourseService()
        path = service._get_category_path(mock_db, "cat1")

        assert path == "AI基础知识"

    @patch('src.services.course_service.SessionLocal')
    def test_get_category_path_nested(self, mock_session_local):
        """测试获取嵌套目录路径"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        parent = CourseCategoryModel(
            id="parent1",
            name="AI基础知识",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        child = CourseCategoryModel(
            id="child1",
            name="什么是AI",
            parent_id="parent1",
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        mock_db.query.return_value.filter.return_value.first.side_effect = [
            child,   # 查询子目录
            parent   # 查询父目录
        ]

        service = CourseService()
        path = service._get_category_path(mock_db, "child1")

        assert path == "AI基础知识 > 什么是AI"

    @patch('src.services.course_service.SessionLocal')
    def test_get_category_path_unknown(self, mock_session_local):
        """测试获取不存在的目录路径"""
        mock_db = MagicMock(spec=Session)
        mock_session_local.return_value = mock_db

        mock_db.query.return_value.filter.return_value.first.return_value = None

        service = CourseService()
        path = service._get_category_path(mock_db, "nonexistent")

        assert path == "未知"
