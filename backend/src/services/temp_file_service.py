# -*- coding: utf-8 -*-
"""临时文件服务"""
import os
import time
import uuid
from pathlib import Path
from typing import Optional
from src.config.temp_files import TempFileConfig
from src.models.temp_files import TempFileUploadResponse


class TempFileService:
    """临时文件服务"""

    def __init__(self):
        self.temp_dir = TempFileConfig.TEMP_DIR
        self.max_size = TempFileConfig.MAX_FILE_SIZE
        self.max_age_seconds = TempFileConfig.MAX_AGE_HOURS * 3600

    def save_file(self, content: bytes, filename: str) -> TempFileUploadResponse:
        """
        保存临时文件

        Args:
            content: 文件内容
            filename: 原始文件名

        Returns:
            TempFileUploadResponse

        Raises:
            ValueError: 文件大小超过限制
        """
        # 检查文件大小
        if len(content) > self.max_size:
            raise ValueError(
                f"文件大小超过限制（最大 {self.max_size // (1024 * 1024)}MB）"
            )

        # 生成唯一ID
        temp_id = str(uuid.uuid4())

        # 保存文件
        file_path = self.temp_dir / f"{temp_id}.tmp"
        with open(file_path, 'wb') as f:
            f.write(content)

        # 生成内容预览（前1000字符）
        content_preview = None
        try:
            text_content = content.decode('utf-8', errors='ignore')
            content_preview = text_content[:1000]
        except Exception:
            pass

        return TempFileUploadResponse(
            temp_id=temp_id,
            filename=filename,
            size=len(content),
            content_preview=content_preview
        )

    def get_file_content(self, temp_id: str) -> Optional[bytes]:
        """
        获取临时文件内容

        Args:
            temp_id: 临时文件ID

        Returns:
            文件内容，不存在返回 None
        """
        file_path = self.temp_dir / f"{temp_id}.tmp"
        if not file_path.exists():
            return None

        with open(file_path, 'rb') as f:
            return f.read()

    def delete_file(self, temp_id: str) -> bool:
        """
        删除临时文件

        Args:
            temp_id: 临时文件ID

        Returns:
            是否删除成功
        """
        file_path = self.temp_dir / f"{temp_id}.tmp"
        if not file_path.exists():
            return False

        try:
            file_path.unlink()
            return True
        except Exception:
            return False

    def cleanup_old_files(self) -> int:
        """
        清理过期的临时文件

        Returns:
            清理的文件数量
        """
        current_time = time.time()
        cleaned_count = 0

        for file_path in self.temp_dir.glob("*.tmp"):
            # 检查文件修改时间
            file_mtime = file_path.stat().st_mtime
            age_seconds = current_time - file_mtime

            if age_seconds > self.max_age_seconds:
                try:
                    file_path.unlink()
                    cleaned_count += 1
                except Exception:
                    pass

        return cleaned_count
