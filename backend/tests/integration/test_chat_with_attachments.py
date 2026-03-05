# -*- coding: utf-8 -*-
"""聊天附件支持测试"""
import pytest
from pathlib import Path
from httpx import AsyncClient
import uuid
from datetime import datetime

from src.db_models_party import KnowledgeCategoryModel, KnowledgeDocumentModel
from src.db_models_party import PartyActivityCategoryModel, PartyActivityDocumentModel
from src.models.temp_files import AttachmentReference


class TestChatWithAttachments:
    """测试聊天附件功能"""

    @pytest.mark.asyncio
    async def test_build_system_prompt_with_attachments_empty(self):
        """测试构建系统提示词（无附件）"""
        from src.services.ai_service import AIService

        ai_service = AIService()
        base_prompt = "你是一个AI助手。"
        result = ai_service.build_system_prompt_with_attachments(base_prompt, [])

        assert result == base_prompt

    @pytest.mark.asyncio
    async def test_build_system_prompt_with_attachments_single(self):
        """测试构建系统提示词（单个附件）"""
        from src.services.ai_service import AIService

        ai_service = AIService()
        base_prompt = "你是一个AI助手。"
        attachments = [
            {"name": "test.txt", "content": "这是测试内容"}
        ]
        result = ai_service.build_system_prompt_with_attachments(base_prompt, attachments)

        assert base_prompt in result
        assert "test.txt" in result
        assert "这是测试内容" in result
        assert "---" in result

    @pytest.mark.asyncio
    async def test_build_system_prompt_with_attachments_multiple(self):
        """测试构建系统提示词（多个附件）"""
        from src.services.ai_service import AIService

        ai_service = AIService()
        base_prompt = "你是一个AI助手。"
        attachments = [
            {"name": "file1.txt", "content": "内容1"},
            {"name": "file2.txt", "content": "内容2"}
        ]
        result = ai_service.build_system_prompt_with_attachments(base_prompt, attachments)

        assert base_prompt in result
        assert "file1.txt" in result
        assert "内容1" in result
        assert "file2.txt" in result
        assert "内容2" in result
        assert "【文件1" in result
        assert "【文件2" in result

    @pytest.mark.asyncio
    async def test_build_system_prompt_with_attachments_long_content(self):
        """测试构建系统提示词（长内容截断）"""
        from src.services.ai_service import AIService

        ai_service = AIService()
        base_prompt = "你是一个AI助手。"
        long_content = "x" * 15000  # 超过10000字符
        attachments = [
            {"name": "long.txt", "content": long_content}
        ]
        result = ai_service.build_system_prompt_with_attachments(base_prompt, attachments)

        assert "long.txt" in result
        assert "因内容过长，后续内容已省略" in result
        assert len(result) < len(base_prompt) + len(long_content)  # 应该被截断

    @pytest.mark.asyncio
    async def test_temp_file_service_integration(self, logged_in_async_client: AsyncClient):
        """测试临时文件服务集成"""
        file_content = "test content".encode('utf-8')
        response = await logged_in_async_client.post(
            "/api/v1/temp_files/upload",
            files={"file": ("test.txt", file_content, "text/plain")}
        )
        assert response.status_code == 200
        temp_data = response.json()
        assert "temp_id" in temp_data

    @pytest.mark.asyncio
    async def test_knowledge_batch_endpoint(self, logged_in_async_client: AsyncClient, async_db_session):
        """测试知识库批量端点集成"""
        # 创建知识库文档
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

        uploads_dir = Path("uploads/knowledge/markdown")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        test_file = uploads_dir / f"{uuid.uuid4()}.md"
        test_file.write_text("# 党建知识\n\n这是重要的党建知识内容。", encoding="utf-8")

        doc = KnowledgeDocumentModel(
            id=str(uuid.uuid4()),
            category_id=category.id,
            filename=test_file.name,
            original_filename="party_knowledge.md",
            markdown_path=str(test_file),
            file_type="markdown",
            file_size=50,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        async_db_session.add(doc)
        await async_db_session.commit()

        # 测试批量获取
        response = await logged_in_async_client.post(
            "/api/v1/knowledge/documents/batch",
            json={"document_ids": [doc.id]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 1
        assert data["documents"][0]["filename"] == "party_knowledge.md"

    @pytest.mark.asyncio
    async def test_party_activity_batch_endpoint(self, logged_in_async_client: AsyncClient, async_db_session):
        """测试党建活动批量端点集成"""
        # 创建党建活动文档
        category = PartyActivityCategoryModel(
            id=str(uuid.uuid4()),
            name="活动目录",
            parent_id=None,
            order=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        async_db_session.add(category)
        await async_db_session.commit()

        uploads_dir = Path("uploads/party-activity/markdown")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        test_file = uploads_dir / f"{uuid.uuid4()}.md"
        test_file.write_text("# 三会一课记录\n\n会议时间：2026年3月5日", encoding="utf-8")

        doc = PartyActivityDocumentModel(
            id=str(uuid.uuid4()),
            category_id=category.id,
            filename=test_file.name,
            original_filename="meeting_record.md",
            markdown_path=str(test_file),
            file_type="markdown",
            file_size=40,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        async_db_session.add(doc)
        await async_db_session.commit()

        # 测试批量获取
        response = await logged_in_async_client.post(
            "/api/v1/party-activities/documents/batch",
            json={"document_ids": [doc.id]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 1
        assert data["documents"][0]["filename"] == "meeting_record.md"
