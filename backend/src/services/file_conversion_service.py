# -*- coding: utf-8 -*-
"""文件转换服务"""
import os
import subprocess
import tempfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """文件转换错误"""
    pass


class FileConversionService:
    """文件转换服务"""

    EXTENSION_MAP = {
        "word": [".docx"],
        "excel": [".xlsx"],
        "pdf": [".pdf"],
        "markdown": [".md"],
        "text": [".txt"],
        "image": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    }

    def _get_file_type(self, filename: str) -> str | None:
        """根据文件名获取文件类型"""
        ext = Path(filename).suffix.lower()
        for file_type, extensions in self.EXTENSION_MAP.items():
            if ext in extensions:
                return file_type
        return None

    async def convert_to_markdown(self, file_path: str, file_type: str) -> str:
        """将文件转换为 Markdown 格式"""
        if file_type == "markdown":
            return Path(file_path).read_text(encoding="utf-8")
        elif file_type == "text":
            content = Path(file_path).read_text(encoding="utf-8")
            return f"```\n{content}\n```"
        elif file_type == "word":
            return await self._convert_word(file_path)
        elif file_type == "excel":
            return await self._convert_excel(file_path)
        elif file_type == "image":
            raise ConversionError("图片文件不支持转换")
        else:
            raise ConversionError(f"不支持的文件类型: {file_type}")

    async def _convert_word(self, file_path: str) -> str:
        """转换 Word 文档"""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            tmp_path = tmp.name

        result = subprocess.run(
            ["pandoc", "-f", "docx", "-t", "markdown", "-o", tmp_path, file_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise ConversionError(f"Word 文档转换失败: {result.stderr}")

        content = Path(tmp_path).read_text(encoding="utf-8")
        os.unlink(tmp_path)
        return content

    async def _convert_excel(self, file_path: str) -> str:
        """转换 Excel 文件"""
        from openpyxl import load_workbook

        wb = load_workbook(file_path, read_only=True)
        lines = []

        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            lines.append(f"\n## {sheet_name}\n")
            for row in ws.iter_rows(values_only=True):
                row_text = "| " + " | ".join(str(cell) if cell is not None else "" for cell in row) + " |"
                lines.append(row_text)

        wb.close()
        return "\n".join(lines)
