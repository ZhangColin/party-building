# -*- coding: utf-8 -*-
"""测试Artifact实体"""
import pytest
from src.domain.entities.artifact import Artifact
from datetime import datetime


def test_artifact_creation():
    """测试创建Artifact实体"""
    now = datetime.now()
    artifact = Artifact(
        id="artifact-123",
        type="html",
        content="<html><body>Test</body></html>",
        created_at=now
    )

    assert artifact.id == "artifact-123"
    assert artifact.type == "html"
    assert artifact.content == "<html><body>Test</body></html>"
    assert artifact.created_at == now


def test_artifact_with_svg_type():
    """测试SVG类型的Artifact"""
    now = datetime.now()
    svg_content = '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40"/></svg>'
    artifact = Artifact(
        id="artifact-svg-1",
        type="svg",
        content=svg_content,
        created_at=now
    )

    assert artifact.type == "svg"
    assert "<svg" in artifact.content
    assert "<circle" in artifact.content


def test_artifact_with_markdown_type():
    """测试Markdown类型的Artifact"""
    now = datetime.now()
    markdown_content = "# Title\n\nThis is a **bold** text."
    artifact = Artifact(
        id="artifact-md-1",
        type="markdown",
        content=markdown_content,
        created_at=now
    )

    assert artifact.type == "markdown"
    assert artifact.content.startswith("# Title")


def test_artifact_attributes():
    """测试Artifact所有属性"""
    now = datetime.now()
    artifact = Artifact(
        id="test-artifact-id",
        type="html",
        content="<p>Test content</p>",
        created_at=now
    )

    # 验证所有属性都被正确设置
    assert hasattr(artifact, 'id')
    assert hasattr(artifact, 'type')
    assert hasattr(artifact, 'content')
    assert hasattr(artifact, 'created_at')

    # 验证属性类型
    assert isinstance(artifact.id, str)
    assert isinstance(artifact.type, str)
    assert isinstance(artifact.content, str)
    assert isinstance(artifact.created_at, datetime)


def test_artifact_empty_content():
    """测试空内容的Artifact"""
    now = datetime.now()
    artifact = Artifact(
        id="artifact-empty",
        type="html",
        content="",
        created_at=now
    )

    assert artifact.content == ""
    assert artifact.type == "html"


def test_artifact_large_content():
    """测试大内容的Artifact"""
    now = datetime.now()
    large_content = "<html>" + "<div>Content</div>" * 1000 + "</html>"
    artifact = Artifact(
        id="artifact-large",
        type="html",
        content=large_content,
        created_at=now
    )

    assert len(artifact.content) > 10000
    assert artifact.type == "html"
