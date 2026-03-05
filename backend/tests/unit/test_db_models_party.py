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
