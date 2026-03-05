# -*- coding: utf-8 -*-
"""模型导出"""
# 从 models.py 模块导入所有模型
# 注意：由于存在同名包 models/ 和模块 models.py，Python会优先导入包
# 因此需要在 __init__.py 中显式导入 models.py 的内容
import sys
from pathlib import Path

# 获取 models.py 模块的路径
models_py_path = Path(__file__).parent.parent / "models.py"

# 动态导入 models.py 模块
import importlib.util
spec = importlib.util.spec_from_file_location("src.models_py", str(models_py_path))
models_py = importlib.util.module_from_spec(spec)
sys.modules["src.models_py"] = models_py
spec.loader.exec_module(models_py)

# 将 models.py 中的所有导出复制到当前命名空间
# 这样 from src.models import XXX 就能正确工作
for name in dir(models_py):
    if not name.startswith("_") and name[0].isupper():
        globals()[name] = getattr(models_py, name)

# 从 temp_files 子模块导入
from .temp_files import AttachmentReference, TempFileUploadResponse

__all__ = ["TempFileUploadResponse", "AttachmentReference"]
