# -*- coding: utf-8 -*-
"""测试知识库服务"""
import pytest
import asyncio
from src.services.knowledge_service import KnowledgeService


def run_async(coro):
    """辅助函数：在同步上下文中运行异步代码"""
    return asyncio.run(coro)


@pytest.mark.asyncio
async def test_create_category(db_session):
    """测试创建目录"""
    service = KnowledgeService(db_session)
    result = await service.create_category("党章学习")

    assert result["name"] == "党章学习"
    assert result["id"] is not None


@pytest.mark.asyncio
async def test_create_document(db_session):
    """测试新建 Markdown 文件"""
    service = KnowledgeService(db_session)

    # 先创建目录
    category = await service.create_category("测试分类")

    # 创建文档
    result = await service.create_document(
        category_id=category["id"],
        filename="新文档.md",
        content="# 新文档\n\n内容"
    )

    assert result["original_filename"] == "新文档.md"
    assert result["file_type"] == "markdown"


@pytest.mark.asyncio
async def test_get_category_tree(db_session):
    """测试获取目录树"""
    service = KnowledgeService(db_session)

    # 创建父目录
    parent = await service.create_category("父目录")

    # 创建子目录
    await service.create_category("子目录", parent_id=parent["id"])

    # 获取目录树
    tree = await service.get_category_tree()

    assert len(tree) == 1
    assert tree[0]["name"] == "父目录"
    assert len(tree[0]["children"]) == 1
    assert tree[0]["children"][0]["name"] == "子目录"


@pytest.mark.asyncio
async def test_delete_document(db_session):
    """测试删除文件"""
    service = KnowledgeService(db_session)

    # 创建目录和文档
    category = await service.create_category("测试分类")
    document = await service.create_document(
        category_id=category["id"],
        filename="测试.md",
        content="# 测试"
    )

    # 删除文档
    result = await service.delete_document(document["id"])
    assert result is True
