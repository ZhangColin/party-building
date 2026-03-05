# -*- coding: utf-8 -*-
"""测试文件转换服务"""
import pytest
from pathlib import Path
from src.services.file_conversion_service import FileConversionService, ConversionError


@pytest.mark.asyncio
async def test_convert_markdown_file(tmp_path):
    """测试 Markdown 文件转换"""
    service = FileConversionService()
    test_file = tmp_path / "test.md"
    test_file.write_text("# Hello\n\nThis is a test.", encoding="utf-8")

    result = await service.convert_to_markdown(str(test_file), "markdown")
    assert result == "# Hello\n\nThis is a test."


@pytest.mark.asyncio
async def test_convert_text_file(tmp_path):
    """测试文本文件转换"""
    service = FileConversionService()
    test_file = tmp_path / "test.txt"
    test_file.write_text("Plain text content", encoding="utf-8")

    result = await service.convert_to_markdown(str(test_file), "text")
    assert "Plain text content" in result


@pytest.mark.asyncio
async def test_convert_unsupported_file(tmp_path):
    """测试不支持的文件类型"""
    service = FileConversionService()
    test_file = tmp_path / "test.png"
    test_file.write_bytes(b"fake image data")

    with pytest.raises(ConversionError, match="图片文件不支持转换"):
        await service.convert_to_markdown(str(test_file), "image")


def test_get_file_type():
    """测试获取文件类型"""
    service = FileConversionService()
    assert service._get_file_type("test.docx") == "word"
    assert service._get_file_type("test.xlsx") == "excel"
    assert service._get_file_type("test.pdf") == "pdf"
    assert service._get_file_type("test.md") == "markdown"
    assert service._get_file_type("test.txt") == "text"
    assert service._get_file_type("test.png") == "image"
    assert service._get_file_type("test.jpg") == "image"
    assert service._get_file_type("test.unknown") is None
