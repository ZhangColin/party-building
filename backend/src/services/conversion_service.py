"""文档转换服务：处理 Markdown 转 Word 等转换任务"""
import subprocess
import tempfile
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional


class ConversionService:
    """文档转换服务类"""

    def __init__(self):
        """初始化转换服务"""
        # 检查 pandoc 是否可用
        self._check_pandoc_available()

    @staticmethod
    def _preprocess_markdown(markdown_content: str) -> str:
        """
        预处理 Markdown 内容，修复答案格式

        问题：AI 生成的格式如下：
        ```
        1. **答案**：
           **解析**：xxx
        ```
        pandoc 会将其转换为：
        - "1." 作为普通文本
        - "解析" 作为新的段落（不是列表的一部分）

        解决方案：转换为标准列表格式：
        ```
        1. **答案**：[答案内容]
           **解析**：xxx
        ```

        Args:
            markdown_content: 原始 Markdown 内容

        Returns:
            str: 处理后的 Markdown 内容
        """
        # 匹配模式：列表编号 + **答案**：[空或内容]换行+缩进+**解析**：
        # 将其转换为：列表编号 + **答案**：[内容或"见解析"] 两个空格换行+缩进+**解析**：
        processed = re.sub(
            r'(\d+)\.\s*\*\*答案\*\*：\s*\n(\s+)\*\*解析\*\*：',
            r'\1. **答案**：见解析  \n\n\2**解析**：',
            markdown_content
        )

        # 匹配模式：列表编号 + **答案**：内容 换行 缩进 **解析**：
        # 在中间添加两个空格（markdown 的硬换行）+ 两个换行符（段落分隔）
        processed = re.sub(
            r'(\d+)\.\s*\*\*答案\*\*：([^\n]+)\n(\s+)\*\*解析\*\*：',
            r'\1. **答案**：\2  \n\n\3**解析**：',
            processed
        )

        return processed
    
    def _check_pandoc_available(self) -> bool:
        """
        检查 pandoc 是否安装并可用
        
        Returns:
            bool: pandoc 是否可用
            
        Raises:
            RuntimeError: pandoc 不可用时抛出异常
        """
        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True
            else:
                raise RuntimeError("pandoc 命令执行失败")
        except FileNotFoundError:
            raise RuntimeError(
                "pandoc 未安装。请安装 pandoc: https://pandoc.org/installing.html"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("pandoc 命令超时")
    
    def markdown_to_word(
        self, 
        markdown_content: str, 
        filename: Optional[str] = None
    ) -> tuple[bytes, str]:
        """
        将 Markdown 内容转换为 Word 文档
        
        Args:
            markdown_content: Markdown 内容
            filename: 文件名（不含扩展名），默认使用时间戳
            
        Returns:
            tuple[bytes, str]: (Word文件内容, 文件名)
            
        Raises:
            ValueError: 输入内容为空
            RuntimeError: 转换失败
        """
        if not markdown_content or not markdown_content.strip():
            raise ValueError("Markdown 内容不能为空")

        # 预处理 Markdown 内容，修复答案格式
        markdown_content = self._preprocess_markdown(markdown_content)

        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"markdown_{timestamp}"
        
        # 确保文件名安全（移除特殊字符）
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).strip()
        if not filename:
            filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        docx_filename = f"{filename}.docx"
        
        # 创建临时文件
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            input_file = temp_dir_path / "input.md"
            output_file = temp_dir_path / "output.docx"
            
            # 写入 Markdown 内容到临时文件
            input_file.write_text(markdown_content, encoding='utf-8')
            
            # 调用 pandoc 转换
            try:
                result = subprocess.run(
                    [
                        "pandoc",
                        str(input_file),
                        "-o", str(output_file),
                        # 支持多种数学公式语法：
                        # - tex_math_dollars: 支持 $...$ 和 $$...$$ (Markdown 扩展语法)
                        # - tex_math_double_backslash: 支持 \(...\) 和 \[...\] (LaTeX 原生语法)
                        "--from=markdown+tex_math_dollars+tex_math_double_backslash",
                        "--to=docx",
                        "--standalone"
                        # 注意：不使用 --mathml 参数
                        # pandoc 默认使用 OMML (Office Math Markup Language)，这是 Word 原生格式
                        # OMML 比 MathML 更适合 Word，能更好地渲染复杂公式
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr or "未知错误"
                    raise RuntimeError(f"pandoc 转换失败: {error_msg}")
                
                # 读取生成的 Word 文件
                if not output_file.exists():
                    raise RuntimeError("pandoc 未生成输出文件")
                
                word_content = output_file.read_bytes()
                
                return word_content, docx_filename
                
            except subprocess.TimeoutExpired:
                raise RuntimeError("pandoc 转换超时（30秒）")
            except Exception as e:
                raise RuntimeError(f"转换过程出错: {str(e)}")
