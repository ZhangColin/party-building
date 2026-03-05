# -*- coding: utf-8 -*-
"""知识库批量获取API测试"""
import pytest
from pathlib import Path
from httpx import AsyncClient
import uuid
from datetime import datetime

from src.db_models_party import KnowledgeCategoryModel, KnowledgeDocumentModel


class TestKnowledgeBatchAPI:
    """测试知识库批量获取API"""

    @pytest.mark.asyncio
    async def test_batch_get_documents_empty_list(self, logged_in_async_client: AsyncClient, async_db_session):
        """测试空列表批量获取"""
        response = await logged_in_async_client.post(
            "/api/v1/knowledge/documents/batch",
            json={"document_ids": []}
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert data["documents"] == []

    @pytest.mark.asyncio
    async def test_batch_get_documents_success(self, logged_in_async_client: AsyncClient, async_db_session):
        """测试批量获取文档"""
        # 创建测试目录
        category = KnowledgeCategoryModel(
            id=str(uuid.uuid4()),
            name="测试目录",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        async_db_session.add(category)
        await async_db_session.commit()

        # 创建测试文件1
        uploads_dir = Path("uploads/knowledge/markdown")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        test_file1 = uploads_dir / f"{uuid.uuid4()}.md"
        test_file1.write_text("测试内容1", encoding="utf-8")

        # 创建测试文件2
        test_file2 = uploads_dir / f"{uuid.uuid4()}.md"
        test_file2.write_text("测试内容2", encoding="utf-8")

        doc1 = KnowledgeDocumentModel(
            id=str(uuid.uuid4()),
            category_id=category.id,
            filename=test_file1.name,
            original_filename="test1.md",
            markdown_path=str(test_file1),
            file_type="markdown",
            file_size=10,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        async_db_session.add(doc1)

        doc2 = KnowledgeDocumentModel(
            id=str(uuid.uuid4()),
            category_id=category.id,
            filename=test_file2.name,
            original_filename="test2.md",
            markdown_path=str(test_file2),
            file_type="markdown",
            file_size=10,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        async_db_session.add(doc2)
        await async_db_session.commit()

        response = await logged_in_async_client.post(
            "/api/v1/knowledge/documents/batch",
            json={"document_ids": [doc1.id, doc2.id]}
        )
        assert response.status_code == 200
        data = response.json()
        print(f"DEBUG Response data: {data}")
        assert "documents" in data
        assert len(data["documents"]) == 2
        # 由于文档顺序可能不同，我们检查两个文档都存在
        filenames = [doc["filename"] for doc in data["documents"]]
        assert "test1.md" in filenames
        assert "test2.md" in filenames
        contents = [doc["content"] for doc in data["documents"]]
        assert "测试内容1" in contents
        assert "测试内容2" in contents

    @pytest.mark.asyncio
    async def test_batch_get_documents_not_found(self, logged_in_async_client: AsyncClient):
        """测试批量获取不存在的文档"""
        response = await logged_in_async_client.post(
            "/api/v1/knowledge/documents/batch",
            json={"document_ids": ["non-existent-id"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert data["documents"] == []

    @pytest.mark.asyncio
    async def test_batch_get_documents_mixed(self, logged_in_async_client: AsyncClient, async_db_session):
        """测试批量获取包含存在和不存在的文档"""
        # 创建测试目录
        category = KnowledgeCategoryModel(
            id=str(uuid.uuid4()),
            name="测试目录",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        async_db_session.add(category)
        await async_db_session.commit()

        # 创建测试文件
        uploads_dir = Path("uploads/knowledge/markdown")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        test_file = uploads_dir / f"{uuid.uuid4()}.md"
        test_file.write_text("测试内容", encoding="utf-8")

        document = KnowledgeDocumentModel(
            id=str(uuid.uuid4()),
            category_id=category.id,
            filename=test_file.name,
            original_filename="test.md",
            markdown_path=str(test_file),
            file_type="markdown",
            file_size=9,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        async_db_session.add(document)
        await async_db_session.commit()

        response = await logged_in_async_client.post(
            "/api/v1/knowledge/documents/batch",
            json={"document_ids": [document.id, "non-existent-id"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 1
        assert data["documents"][0]["filename"] == "test.md"
