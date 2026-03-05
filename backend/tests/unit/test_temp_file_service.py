# -*- coding: utf-8 -*-
"""临时文件服务单元测试"""
import pytest
from pathlib import Path
from src.services.temp_file_service import TempFileService
from src.config.temp_files import TempFileConfig


@pytest.fixture
def temp_service():
    """创建临时文件服务实例"""
    return TempFileService()


@pytest.fixture
def temp_dir():
    """获取临时文件目录"""
    return TempFileConfig.TEMP_DIR


def test_save_temp_file(temp_service, temp_dir):
    """测试保存临时文件"""
    content = b"test content"
    filename = "test.txt"

    response = temp_service.save_file(content, filename)

    assert response.temp_id
    assert response.filename == filename
    assert response.size == len(content)
    assert response.content_preview == "test content"

    # 验证文件存在
    file_path = temp_dir / f"{response.temp_id}.tmp"
    assert file_path.exists()

    # 清理
    temp_service.delete_file(response.temp_id)


def test_get_temp_file(temp_service, temp_dir):
    """测试获取临时文件内容"""
    content = b"test content for get"
    filename = "test_get.txt"

    save_response = temp_service.save_file(content, filename)
    retrieved_content = temp_service.get_file_content(save_response.temp_id)

    assert retrieved_content == content

    # 清理
    temp_service.delete_file(save_response.temp_id)


def test_get_nonexistent_file(temp_service):
    """测试获取不存在的文件"""
    result = temp_service.get_file_content("nonexistent-id")
    assert result is None


def test_delete_temp_file(temp_service, temp_dir):
    """测试删除临时文件"""
    content = b"test content for delete"
    filename = "test_delete.txt"

    save_response = temp_service.save_file(content, filename)
    file_path = temp_dir / f"{save_response.temp_id}.tmp"

    # 确认文件存在
    assert file_path.exists()

    # 删除文件
    result = temp_service.delete_file(save_response.temp_id)
    assert result is True

    # 确认文件不存在
    assert not file_path.exists()


def test_file_size_limit(temp_service):
    """测试文件大小限制"""
    # 创建一个超过限制的文件（11MB）
    large_content = b"x" * (11 * 1024 * 1024)
    filename = "large.txt"

    with pytest.raises(ValueError, match="文件大小超过限制"):
        temp_service.save_file(large_content, filename)


def test_cleanup_old_files(temp_service, temp_dir):
    """测试清理旧文件"""
    # 创建一些测试文件
    content = b"old content"
    filename = "old.txt"

    save_response = temp_service.save_file(content, filename)
    file_path = temp_dir / f"{save_response.temp_id}.tmp"

    # 修改文件修改时间（模拟旧文件）
    import time
    old_time = time.time() - (2 * 3600)  # 2小时前
    import os
    os.utime(file_path, (old_time, old_time))

    # 执行清理
    cleaned_count = temp_service.cleanup_old_files()

    assert cleaned_count >= 1
    assert not file_path.exists()
