# -*- coding: utf-8 -*-
"""课程文档路由集成测试

测试 courses.py 中的所有端点，目标覆盖率 50%+
"""
import pytest
from io import BytesIO
from datetime import datetime
from src.db_models import CourseCategoryModel, CourseDocumentModel
from sqlalchemy.orm import Session


# ==================== 辅助函数 ====================

def create_test_category(db: Session, name: str = "测试目录", parent_id: str = None, order: int = 1) -> str:
    """创建测试目录"""
    category = CourseCategoryModel(
        name=name,
        parent_id=parent_id,
        order=order
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category.id


def create_test_document(db: Session, category_id: str, title: str = "测试文档", order: int = 1) -> str:
    """创建测试文档"""
    import tempfile
    import os

    # 创建临时文件存储markdown内容
    content = f"# {title}\n\n这是文档内容"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_file_path = f.name

    try:
        document = CourseDocumentModel(
            title=title,
            summary=f"{title}的摘要",
            file_path=temp_file_path,
            category_id=category_id,
            order=order
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document.id
    except Exception:
        # 如果失败，删除临时文件
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise


# ==================== 用户端接口测试 ====================

class TestCourseCategoriesPublic:
    """测试用户端课程目录接口"""

    @pytest.mark.asyncio
    async def test_get_course_category_tree(self, logged_in_client, db_session):
        """测试获取课程目录树"""
        # 创建测试目录
        create_test_category(db_session, "目录1")
        create_test_category(db_session, "目录2")

        response = await logged_in_client.get("/api/v1/documents/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data

    @pytest.mark.asyncio
    async def test_get_course_category_tree_unauthorized(self, async_client):
        """测试未授权访问目录树"""
        response = await async_client.get("/api/v1/documents/categories")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_course_category_tree_server_error(self, logged_in_client, monkeypatch):
        """测试获取目录树时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def get_category_tree(self):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        response = await logged_in_client.get("/api/v1/documents/categories")
        assert response.status_code == 500
        assert "获取课程目录树失败" in response.json()["detail"]


class TestCourseDocumentsPublic:
    """测试用户端课程文档接口"""

    @pytest.mark.asyncio
    async def test_get_documents_by_category(self, logged_in_client, db_session):
        """测试获取指定目录的文档列表"""
        category_id = create_test_category(db_session, "测试目录")
        create_test_document(db_session, category_id, "文档1")

        response = await logged_in_client.get(f"/api/v1/documents/category/{category_id}/documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data

    @pytest.mark.asyncio
    async def test_get_documents_by_category_unauthorized(self, async_client, db_session):
        """测试未授权访问文档列表"""
        category_id = create_test_category(db_session, "测试目录")
        response = await async_client.get(f"/api/v1/documents/category/{category_id}/documents")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_documents_by_category_server_error(self, logged_in_client, db_session, monkeypatch):
        """测试获取文档列表时服务端错误"""
        # 使用 monkeypatch 模拟服务抛出异常
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def get_documents_by_category(self, category_id):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        response = await logged_in_client.get(f"/api/v1/documents/category/{category_id}/documents")
        assert response.status_code == 500
        assert "获取目录文档列表失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_document_detail(self, logged_in_client, db_session):
        """测试获取文档详情"""
        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "测试文档")

        response = await logged_in_client.get(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "content" in data

    @pytest.mark.asyncio
    async def test_get_document_detail_not_found(self, logged_in_client):
        """测试获取不存在的文档"""
        response = await logged_in_client.get("/api/v1/documents/nonexistent-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_document_detail_unauthorized(self, async_client, db_session):
        """测试未授权访问文档详情"""
        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "测试文档")
        response = await async_client.get(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_document_detail_server_error(self, logged_in_client, db_session, monkeypatch):
        """测试获取文档详情时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def get_document_detail(self, doc_id):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "测试文档")
        response = await logged_in_client.get(f"/api/v1/documents/{doc_id}")
        assert response.status_code == 500
        assert "获取文档详情失败" in response.json()["detail"]


# ==================== 管理员接口测试 ====================

class TestAdminCourseCategories:
    """测试管理员课程目录接口"""

    @pytest.mark.asyncio
    async def test_get_admin_categories_success(self, admin_client, db_session):
        """测试管理员获取目录列表"""
        create_test_category(db_session, "目录1")
        create_test_category(db_session, "目录2")

        response = await admin_client.get("/api/v1/admin/course-categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data

    @pytest.mark.asyncio
    async def test_get_admin_categories_forbidden(self, logged_in_client):
        """测试非管理员访问管理接口"""
        response = await logged_in_client.get("/api/v1/admin/course-categories")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_admin_categories_server_error(self, admin_client, monkeypatch):
        """测试获取管理目录列表时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def get_admin_categories(self):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        response = await admin_client.get("/api/v1/admin/course-categories")
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_category(self, admin_client):
        """测试创建目录"""
        response = await admin_client.post(
            "/api/v1/admin/course-categories",
            json={
                "name": "测试目录",
                "description": "这是一个测试目录",
                "parent_id": None,
                "order": 1
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "category" in data

    @pytest.mark.asyncio
    async def test_create_category_invalid_parent(self, admin_client):
        """测试创建目录时父目录不存在"""
        response = await admin_client.post(
            "/api/v1/admin/course-categories",
            json={
                "name": "测试目录",
                "description": "这是一个测试目录",
                "parent_id": "nonexistent-parent",
                "order": 1
            }
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_category_server_error(self, admin_client, monkeypatch):
        """测试创建目录时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def create_category(self, request):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        response = await admin_client.post(
            "/api/v1/admin/course-categories",
            json={
                "name": "测试目录",
                "description": "测试",
                "parent_id": None,
                "order": 1
            }
        )
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_category(self, admin_client, db_session):
        """测试更新目录"""
        category_id = create_test_category(db_session, "原始目录名")
        response = await admin_client.patch(
            f"/api/v1/admin/course-categories/{category_id}",
            json={
                "name": "更新后的目录名",
                "description": "更新后的描述"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "category" in data

    @pytest.mark.asyncio
    async def test_update_category_not_found(self, admin_client):
        """测试更新不存在的目录"""
        response = await admin_client.patch(
            "/api/v1/admin/course-categories/nonexistent-id",
            json={"name": "更新后的目录名"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_category_server_error(self, admin_client, db_session, monkeypatch):
        """测试更新目录时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def update_category(self, category_id, request):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        response = await admin_client.patch(
            f"/api/v1/admin/course-categories/{category_id}",
            json={"name": "新名称"}
        )
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_category(self, admin_client, db_session):
        """测试删除目录"""
        category_id = create_test_category(db_session, "待删除目录")

        response = await admin_client.delete(f"/api/v1/admin/course-categories/{category_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_category_with_children(self, admin_client, db_session):
        """测试删除有子目录的目录（应该失败）"""
        parent_id = create_test_category(db_session, "父目录")
        create_test_category(db_session, "子目录", parent_id=parent_id)

        response = await admin_client.delete(f"/api/v1/admin/course-categories/{parent_id}")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_delete_category_server_error(self, admin_client, db_session, monkeypatch):
        """测试删除目录时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def delete_category(self, category_id):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        response = await admin_client.delete(f"/api/v1/admin/course-categories/{category_id}")
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_move_category_up(self, admin_client, db_session):
        """测试上移目录"""
        cat1_id = create_test_category(db_session, "目录1", order=1)
        cat2_id = create_test_category(db_session, "目录2", order=2)

        response = await admin_client.post(f"/api/v1/admin/course-categories/{cat2_id}/move-up")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_move_category_up_already_first(self, admin_client, db_session):
        """测试上移已经是第一个的目录（应该失败）"""
        category_id = create_test_category(db_session, "第一个目录", order=0)

        response = await admin_client.post(f"/api/v1/admin/course-categories/{category_id}/move-up")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_move_category_up_server_error(self, admin_client, db_session, monkeypatch):
        """测试上移目录时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def move_category_up(self, category_id):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        response = await admin_client.post(f"/api/v1/admin/course-categories/{category_id}/move-up")
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_move_category_down(self, admin_client, db_session):
        """测试下移目录"""
        cat1_id = create_test_category(db_session, "目录A", order=1)
        cat2_id = create_test_category(db_session, "目录B", order=2)

        response = await admin_client.post(f"/api/v1/admin/course-categories/{cat1_id}/move-down")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_move_category_down_already_last(self, admin_client, db_session):
        """测试下移已经是最后一个的目录（应该失败）"""
        category_id = create_test_category(db_session, "最后一个目录", order=999)

        response = await admin_client.post(f"/api/v1/admin/course-categories/{category_id}/move-down")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_move_category_down_server_error(self, admin_client, db_session, monkeypatch):
        """测试下移目录时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def move_category_down(self, category_id):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        response = await admin_client.post(f"/api/v1/admin/course-categories/{category_id}/move-down")
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]


class TestAdminCourseDocuments:
    """测试管理员课程文档接口"""

    @pytest.mark.asyncio
    async def test_get_admin_documents(self, admin_client, db_session):
        """测试获取管理员文档列表"""
        category_id = create_test_category(db_session, "测试目录")
        create_test_document(db_session, category_id, "文档1")

        response = await admin_client.get("/api/v1/admin/course-documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert "page" in data

    @pytest.mark.asyncio
    async def test_get_admin_documents_with_pagination(self, admin_client, db_session):
        """测试分页获取文档列表"""
        category_id = create_test_category(db_session, "测试目录")
        create_test_document(db_session, category_id, "文档1")

        response = await admin_client.get("/api/v1/admin/course-documents?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_get_admin_documents_forbidden(self, logged_in_client):
        """测试非管理员访问文档管理接口"""
        response = await logged_in_client.get("/api/v1/admin/course-documents")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_admin_documents_server_error(self, admin_client, monkeypatch):
        """测试获取管理文档列表时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def get_admin_documents(self, page, page_size, category_id):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        response = await admin_client.get("/api/v1/admin/course-documents")
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_document(self, admin_client, db_session):
        """测试创建文档"""
        category_id = create_test_category(db_session, "测试目录")
        markdown_content = "# 测试文档\n\n这是一个测试文档的内容。"

        files = {
            "markdown_file": ("test.md", BytesIO(markdown_content.encode('utf-8')), "text/markdown")
        }
        data = {
            "title": "测试文档标题",
            "summary": "这是一个测试文档",
            "category_id": category_id,
            "order": 1
        }

        response = await admin_client.post(
            "/api/v1/admin/course-documents",
            files=files,
            data=data
        )
        assert response.status_code == 201
        result = response.json()
        assert "document" in result

    @pytest.mark.asyncio
    async def test_create_document_invalid_file_type(self, admin_client, db_session):
        """测试创建文档时上传无效文件类型"""
        category_id = create_test_category(db_session, "测试目录")

        files = {
            "markdown_file": ("test.txt", BytesIO(b"not markdown"), "text/plain")
        }
        data = {
            "title": "测试文档",
            "summary": "测试",
            "category_id": category_id
        }

        response = await admin_client.post(
            "/api/v1/admin/course-documents",
            files=files,
            data=data
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_document_file_too_large(self, admin_client, db_session):
        """测试创建文档时文件过大"""
        category_id = create_test_category(db_session, "测试目录")

        # 创建超过5MB的文件
        large_content = "x" * (6 * 1024 * 1024)  # 6MB
        files = {
            "markdown_file": ("large.md", BytesIO(large_content.encode('utf-8')), "text/markdown")
        }
        data = {
            "title": "大文件测试",
            "summary": "测试",
            "category_id": category_id
        }

        response = await admin_client.post(
            "/api/v1/admin/course-documents",
            files=files,
            data=data
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_document_invalid_category(self, admin_client):
        """测试创建文档时目录不存在"""
        markdown_content = "# Test"
        files = {
            "markdown_file": ("test.md", BytesIO(markdown_content.encode('utf-8')), "text/markdown")
        }
        data = {
            "title": "测试文档",
            "summary": "测试",
            "category_id": "nonexistent-category"
        }

        response = await admin_client.post(
            "/api/v1/admin/course-documents",
            files=files,
            data=data
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_document_unsupported_extension(self, admin_client, db_session):
        """测试创建文档时文件扩展名不支持"""
        category_id = create_test_category(db_session, "测试目录")

        # 使用.markdown扩展名（支持的）
        content = "# Test"
        files = {
            "markdown_file": ("test.markdown", BytesIO(content.encode('utf-8')), "text/markdown")
        }
        data = {
            "title": "测试文档",
            "summary": "测试",
            "category_id": category_id
        }

        response = await admin_client.post(
            "/api/v1/admin/course-documents",
            files=files,
            data=data
        )
        # 应该成功创建
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_document_server_error(self, admin_client, db_session, monkeypatch):
        """测试创建文档时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def create_document(self, **kwargs):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        markdown_content = "# Test"
        files = {
            "markdown_file": ("test.md", BytesIO(markdown_content.encode('utf-8')), "text/markdown")
        }
        data = {
            "title": "测试文档",
            "summary": "测试",
            "category_id": category_id
        }

        response = await admin_client.post(
            "/api/v1/admin/course-documents",
            files=files,
            data=data
        )
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_document(self, admin_client, db_session):
        """测试更新文档"""
        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "原始标题")

        response = await admin_client.patch(
            f"/api/v1/admin/course-documents/{doc_id}",
            json={
                "title": "更新后的标题",
                "summary": "更新后的摘要"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "document" in data

    @pytest.mark.asyncio
    async def test_update_document_not_found(self, admin_client):
        """测试更新不存在的文档"""
        response = await admin_client.patch(
            "/api/v1/admin/course-documents/nonexistent-id",
            json={"title": "新标题"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_document_server_error(self, admin_client, db_session, monkeypatch):
        """测试更新文档时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def update_document(self, doc_id, request):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "测试文档")

        response = await admin_client.patch(
            f"/api/v1/admin/course-documents/{doc_id}",
            json={"title": "新标题"}
        )
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_document(self, admin_client, db_session):
        """测试删除文档"""
        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "待删除文档")

        response = await admin_client.delete(f"/api/v1/admin/course-documents/{doc_id}")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_document_server_error(self, admin_client, db_session, monkeypatch):
        """测试删除文档时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def delete_document(self, doc_id):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "测试文档")

        response = await admin_client.delete(f"/api/v1/admin/course-documents/{doc_id}")
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_move_document_up(self, admin_client, db_session):
        """测试上移文档"""
        category_id = create_test_category(db_session, "测试目录")
        doc1_id = create_test_document(db_session, category_id, "文档1", order=1)
        doc2_id = create_test_document(db_session, category_id, "文档2", order=2)

        response = await admin_client.post(f"/api/v1/admin/course-documents/{doc2_id}/move-up")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_move_document_up_already_first(self, admin_client, db_session):
        """测试上移已经是第一个的文档（应该失败）"""
        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "第一个文档", order=0)

        response = await admin_client.post(f"/api/v1/admin/course-documents/{doc_id}/move-up")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_move_document_up_server_error(self, admin_client, db_session, monkeypatch):
        """测试上移文档时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def move_document_up(self, doc_id):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "测试文档")

        response = await admin_client.post(f"/api/v1/admin/course-documents/{doc_id}/move-up")
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_move_document_down(self, admin_client, db_session):
        """测试下移文档"""
        category_id = create_test_category(db_session, "测试目录")
        doc1_id = create_test_document(db_session, category_id, "文档A", order=1)
        doc2_id = create_test_document(db_session, category_id, "文档B", order=2)

        response = await admin_client.post(f"/api/v1/admin/course-documents/{doc1_id}/move-down")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_move_document_down_already_last(self, admin_client, db_session):
        """测试下移已经是最后一个的文档（应该失败）"""
        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "最后一个文档", order=999)

        response = await admin_client.post(f"/api/v1/admin/course-documents/{doc_id}/move-down")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_move_document_down_server_error(self, admin_client, db_session, monkeypatch):
        """测试下移文档时服务端错误"""
        from src.routers.dependencies import get_course_service

        def mock_get_service():
            class MockService:
                def move_document_down(self, doc_id):
                    raise Exception("数据库连接失败")

            return MockService()

        monkeypatch.setattr("src.interfaces.routers.courses.courses.get_course_service", mock_get_service)

        category_id = create_test_category(db_session, "测试目录")
        doc_id = create_test_document(db_session, category_id, "测试文档")

        response = await admin_client.post(f"/api/v1/admin/course-documents/{doc_id}/move-down")
        assert response.status_code == 500
        assert "数据库连接失败" in response.json()["detail"]


class TestRequireAdminFunction:
    """测试 require_admin 权限验证函数"""

    @pytest.mark.asyncio
    async def test_require_admin_with_admin_user(self, admin_client):
        """测试管理员用户通过权限验证"""
        # 这个测试通过其他管理员接口间接测试
        response = await admin_client.get("/api/v1/admin/course-categories")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_require_admin_with_regular_user(self, logged_in_client):
        """测试普通用户被权限验证拒绝"""
        response = await logged_in_client.get("/api/v1/admin/course-categories")
        assert response.status_code == 403
        assert response.json()["detail"] == "需要管理员权限"
