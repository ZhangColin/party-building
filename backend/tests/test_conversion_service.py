"""测试 ConversionService 的预处理功能"""
import pytest
from src.services.conversion_service import ConversionService


class TestMarkdownPreprocessing:
    """测试 Markdown 预处理功能"""

    def test_answer_with_no_content(self):
        """测试空答案字段的换行处理"""
        markdown = """1. **答案**：
   **解析**：根据题意，我们可以得到两个方程："""

        service = ConversionService()
        processed = service._preprocess_markdown(markdown)

        print("=== 空答案处理结果 ===")
        print(processed)
        print("======================")

        # 应该转换为标准格式
        assert '1. **答案**：见解析' in processed
        assert '\n\n' in processed  # 应该有空行

    def test_answer_with_content(self):
        """测试有内容答案字段的换行处理"""
        markdown = """1. **答案**：B
   **解析**：将点代入得到方程组："""

        service = ConversionService()
        processed = service._preprocess_markdown(markdown)

        print("=== 有答案处理结果 ===")
        print(processed)
        print("======================")

        # 应该保留答案内容
        assert '1. **答案**：B' in processed
        assert '\n\n' in processed  # 应该有空行
        # 解析应该在缩进后
        assert '  **解析**' in processed

    def test_preserve_other_content(self):
        """测试不修改其他内容"""
        markdown = """### 一、选择题

1. **答案**：B
   **解析**：这是解析。

### 二、填空题

1. **答案**：3
   **解析**：这是填空题解析。"""

        service = ConversionService()
        processed = service._preprocess_markdown(markdown)

        # 应该保留标题
        assert '### 一、选择题' in processed
        assert '### 二、填空题' in processed

        # 应该添加换行
        assert processed.count('\n\n') >= 2
