# -*- coding: utf-8 -*-
"""ConversionService 单元测试"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.services.conversion_service import ConversionService


class TestConversionService:
    """ConversionService 测试类"""

    def test_init_pandoc_available(self):
        """测试初始化 - pandoc 可用"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            service = ConversionService()
            mock_run.assert_called_once_with(
                ["pandoc", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert service is not None

    def test_init_pandoc_not_found(self):
        """测试初始化 - pandoc 未安装"""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            with pytest.raises(RuntimeError) as exc_info:
                ConversionService()
            assert "pandoc 未安装" in str(exc_info.value)

    def test_init_pandoc_timeout(self):
        """测试初始化 - pandoc 命令超时"""
        from subprocess import TimeoutExpired

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = TimeoutExpired("pandoc", 5)
            with pytest.raises(RuntimeError) as exc_info:
                ConversionService()
            assert "pandoc 命令超时" in str(exc_info.value)

    def test_init_pandoc_fails(self):
        """测试初始化 - pandoc 命令执行失败"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            with pytest.raises(RuntimeError) as exc_info:
                ConversionService()
            assert "pandoc 命令执行失败" in str(exc_info.value)

    def test_preprocess_markdown_empty_answer(self):
        """测试预处理 - 空答案格式"""
        markdown = """1. **答案**：
   **解析**：这是解析内容"""
        result = ConversionService._preprocess_markdown(markdown)
        assert "见解析" in result
        assert "**解析**：这是解析内容" in result

    def test_preprocess_markdown_with_answer(self):
        """测试预处理 - 带答案内容"""
        markdown = """1. **答案**：这是答案
   **解析**：这是解析"""
        result = ConversionService._preprocess_markdown(markdown)
        assert "**答案**：这是答案  " in result
        assert "**解析**：这是解析" in result
        # 验证有硬换行和段落分隔
        assert "  \n\n" in result

    def test_preprocess_markdown_multiple_questions(self):
        """测试预处理 - 多个题目"""
        markdown = """1. **答案**：答案1
   **解析**：解析1

2. **答案**：
   **解析**：解析2

3. **答案**：答案3
   **解析**：解析3"""
        result = ConversionService._preprocess_markdown(markdown)
        # 验证第1题
        assert "1. **答案**：答案1" in result
        assert "解析1" in result
        # 验证第2题（空答案）
        assert "2. **答案**：见解析" in result
        assert "解析2" in result
        # 验证第3题
        assert "3. **答案**：答案3" in result
        assert "解析3" in result

    def test_preprocess_markdown_no_change(self):
        """测试预处理 - 无需修改的内容"""
        markdown = "# 标题\n\n普通段落内容"
        result = ConversionService._preprocess_markdown(markdown)
        assert result == markdown

    @patch("src.services.conversion_service.subprocess.run")
    def test_markdown_to_word_empty_content(self, mock_run):
        """测试转换 - 空内容"""
        mock_run.return_value = MagicMock(returncode=0)
        service = ConversionService()
        with pytest.raises(ValueError) as exc_info:
            service.markdown_to_word("")
        assert "Markdown 内容不能为空" in str(exc_info.value)

    @patch("src.services.conversion_service.subprocess.run")
    def test_markdown_to_word_whitespace_only(self, mock_run):
        """测试转换 - 仅空白字符"""
        mock_run.return_value = MagicMock(returncode=0)
        service = ConversionService()
        with pytest.raises(ValueError) as exc_info:
            service.markdown_to_word("   \n\n  ")
        assert "Markdown 内容不能为空" in str(exc_info.value)

    @patch("src.services.conversion_service.Path.read_bytes")
    @patch("src.services.conversion_service.Path.write_text")
    @patch("src.services.conversion_service.Path.exists")
    @patch("src.services.conversion_service.subprocess.run")
    def test_markdown_to_word_default_filename(self, mock_run, mock_exists, mock_write, mock_read):
        """测试转换 - 默认文件名"""
        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True
        mock_read.return_value = b"fake docx content"

        service = ConversionService()
        content, filename = service.markdown_to_word("# 测试")

        assert content == b"fake docx content"
        assert filename.endswith(".docx")
        # 验证文件名包含时间戳
        assert "markdown_" in filename

    @patch("src.services.conversion_service.Path.read_bytes")
    @patch("src.services.conversion_service.Path.write_text")
    @patch("src.services.conversion_service.Path.exists")
    @patch("src.services.conversion_service.subprocess.run")
    def test_markdown_to_word_custom_filename(self, mock_run, mock_exists, mock_write, mock_read):
        """测试转换 - 自定义文件名"""
        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True
        mock_read.return_value = b"fake docx content"

        service = ConversionService()
        content, filename = service.markdown_to_word("# 测试", "my_doc")

        assert content == b"fake docx content"
        assert filename == "my_doc.docx"

    @patch("src.services.conversion_service.Path.read_bytes")
    @patch("src.services.conversion_service.Path.write_text")
    @patch("src.services.conversion_service.Path.exists")
    @patch("src.services.conversion_service.subprocess.run")
    def test_markdown_to_word_sanitizes_filename(self, mock_run, mock_exists, mock_write, mock_read):
        """测试转换 - 清理文件名中的特殊字符"""
        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True
        mock_read.return_value = b"fake docx content"

        service = ConversionService()
        content, filename = service.markdown_to_word("# 测试", "test@#$%.docx")

        # 特殊字符应被移除
        assert "@" not in filename
        assert "#" not in filename
        assert "$" not in filename
        assert "%" not in filename
        assert filename.endswith(".docx")

    @patch("src.services.conversion_service.Path.read_bytes")
    @patch("src.services.conversion_service.Path.write_text")
    @patch("src.services.conversion_service.Path.exists")
    @patch("src.services.conversion_service.subprocess.run")
    def test_markdown_to_word_empty_after_sanitization(self, mock_run, mock_exists, mock_write, mock_read):
        """测试转换 - 文件名清理后为空"""
        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True
        mock_read.return_value = b"fake docx content"

        service = ConversionService()
        content, filename = service.markdown_to_word("# 测试", "@#$%")

        # 应使用默认文件名
        assert filename.startswith("document_")
        assert filename.endswith(".docx")

    @patch("src.services.conversion_service.subprocess.run", return_value=MagicMock(returncode=0))
    def test_markdown_to_word_pandoc_fails(self, mock_run_init):
        """测试转换 - pandoc 转换失败"""
        with patch("src.services.conversion_service.subprocess.run") as mock_run:
            # 第一次调用（初始化）成功，第二次调用（转换）失败
            mock_run.side_effect = [
                MagicMock(returncode=0),  # 初始化
                MagicMock(returncode=1, stderr="pandoc error")  # 转换
            ]

            with patch("src.services.conversion_service.Path.exists", return_value=True):
                service = ConversionService()
                with pytest.raises(RuntimeError) as exc_info:
                    service.markdown_to_word("# 测试")
                assert "pandoc 转换失败" in str(exc_info.value)

    def test_markdown_to_word_no_output_file(self):
        """测试转换 - pandoc 未生成输出文件"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("pathlib.Path.exists") as mock_exists:
                mock_exists.return_value = False

                service = ConversionService()
                with pytest.raises(RuntimeError) as exc_info:
                    service.markdown_to_word("# 测试")
                assert "pandoc 未生成输出文件" in str(exc_info.value)

    @patch("src.services.conversion_service.subprocess.run", return_value=MagicMock(returncode=0))
    def test_markdown_to_word_timeout(self, mock_run_init):
        """测试转换 - pandoc 超时"""
        from subprocess import TimeoutExpired

        with patch("src.services.conversion_service.subprocess.run") as mock_run:
            # 第一次调用（初始化）成功，第二次调用（转换）超时
            mock_run.side_effect = [
                MagicMock(returncode=0),  # 初始化
                TimeoutExpired("pandoc", 30)  # 转换超时
            ]

            with patch("src.services.conversion_service.Path.exists", return_value=True):
                service = ConversionService()
                with pytest.raises(RuntimeError) as exc_info:
                    service.markdown_to_word("# 测试")
                assert "pandoc 转换超时" in str(exc_info.value)

    @patch("src.services.conversion_service.Path.read_bytes")
    @patch("src.services.conversion_service.Path.write_text")
    @patch("src.services.conversion_service.Path.exists")
    @patch("src.services.conversion_service.subprocess.run")
    def test_markdown_to_word_with_math(self, mock_run, mock_exists, mock_write, mock_read):
        """测试转换 - 包含数学公式"""
        markdown = "# 数学测试\n\n行内公式 $E=mc^2$\n\n块级公式 $$\n\\int_0^1 x dx\n$$"

        mock_run.return_value = MagicMock(returncode=0)
        mock_exists.return_value = True
        mock_read.return_value = b"fake docx with math"

        service = ConversionService()
        content, filename = service.markdown_to_word(markdown)

        # 验证 pandoc 参数包含数学扩展
        call_args = mock_run.call_args[0][0]
        assert "--from=markdown+tex_math_dollars+tex_math_double_backslash" in call_args
        assert content == b"fake docx with math"
