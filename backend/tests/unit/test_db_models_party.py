# -*- coding: utf-8 -*-
"""测试党建业务数据模型"""
import pytest
from src.db_models_party import KnowledgeCategoryModel, KnowledgeDocumentModel


def test_knowledge_category_model_creation(db_session):
    """测试创建知识库目录"""
    category = KnowledgeCategoryModel(name="党章学习")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    assert category.id is not None
    assert category.name == "党章学习"
    assert category.parent_id is None
    assert category.order == 0


def test_knowledge_category_tree_structure(db_session):
    """测试目录树形结构"""
    parent = KnowledgeCategoryModel(name="党建学习")
    db_session.add(parent)
    db_session.commit()
    db_session.refresh(parent)

    child = KnowledgeCategoryModel(name="党章学习", parent_id=parent.id)
    db_session.add(child)
    db_session.commit()
    db_session.refresh(parent)
    db_session.refresh(child)

    assert parent.children is not None
    assert len(parent.children) == 1
    assert parent.children[0].name == "党章学习"


def test_knowledge_document_model_creation(db_session):
    """测试创建知识库文档"""
    category = KnowledgeCategoryModel(name="测试分类")
    db_session.add(category)
    db_session.commit()

    document = KnowledgeDocumentModel(
        category_id=category.id,
        filename="test.md",
        original_filename="test.md",
        file_type="markdown",
        file_size=1024
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    assert document.id is not None
    assert document.filename == "test.md"
    assert document.category_id == category.id


def test_party_activity_category_model(db_session):
    """测试党建活动目录模型"""
    from src.db_models_party import PartyActivityCategoryModel

    category = PartyActivityCategoryModel(name="三会一课")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)

    assert category.id is not None
    assert category.name == "三会一课"
    assert category.parent_id is None
