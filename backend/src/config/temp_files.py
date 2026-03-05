# -*- coding: utf-8 -*-
"""临时文件配置"""
from pathlib import Path

# 临时文件目录（相对于 backend 目录）
# 从 config/temp_files.py -> backend/src/config -> backend/src -> backend -> uploads/temp
_TEMP_DIR = Path(__file__).parent.parent.parent / "uploads" / "temp"


class TempFileConfig:
    """临时文件配置"""
    # 临时文件目录
    TEMP_DIR = _TEMP_DIR
    # 最大文件大小（字节）
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    # 清理间隔（小时）
    CLEANUP_INTERVAL_HOURS = 1
    # 文件最大存活时间（小时）
    MAX_AGE_HOURS = 1

    @classmethod
    def ensure_temp_dir(cls):
        """确保临时文件目录存在"""
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)


# 启动时确保目录存在
TempFileConfig.ensure_temp_dir()
