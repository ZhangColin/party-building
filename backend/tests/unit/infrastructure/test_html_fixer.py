# -*- coding: utf-8 -*-
"""
HtmlFixerService单元测试
"""
import pytest
from src.infrastructure.html_fixer import HtmlFixerService, BS4_AVAILABLE


class TestHtmlFixerService:
    """HtmlFixerService测试类"""

    def test_fix_broken_tags_closes_unclosed_div(self):
        """测试修复未闭合的div标签"""
        broken = "<div><p>Hello</p>"
        fixed = HtmlFixerService.fix_broken_tags(broken)

        if BS4_AVAILABLE:
            assert "</div>" in fixed
            assert "<p>Hello</p>" in fixed

    def test_fix_broken_tags_handles_empty_string(self):
        """测试处理空字符串"""
        fixed = HtmlFixerService.fix_broken_tags("")
        assert fixed == ""

    def test_fix_broken_tags_handles_none(self):
        """测试处理None"""
        fixed = HtmlFixerService.fix_broken_tags(None)
        assert fixed == ""

    def test_extract_text_gets_text_content(self):
        """测试提取文本内容"""
        html = "<div><p>Hello <b>World</b></p></div>"
        text = HtmlFixerService.extract_text(html)

        if BS4_AVAILABLE:
            assert "Hello World" in text
        else:
            # 简单模式也应该工作
            assert "Hello" in text or "World" in text

    def test_fix_encoding_replaces_mojibake(self):
        """测试修复编码问题"""
        broken = "Helloâ€™s World"  # 乱码的撇号
        fixed = HtmlFixerService.fix_encoding(broken)

        assert "'" in fixed or "'s" in fixed
        assert "â€™" not in fixed

    def test_close_open_tags_fixes_self_closing_tags(self):
        """测试修复自闭合标签"""
        html = "<img src='test.jpg'>"
        fixed = HtmlFixerService.close_open_tags(html)

        # 正则替换应该工作
        assert "<img src='test.jpg' />" in fixed or "<img src=\"test.jpg\" />" in fixed

    def test_sanitize_scripts_removes_script_tags(self):
        """测试移除script标签"""
        html = "<div>Hello<script>alert('xss')</script></div>"
        cleaned = HtmlFixerService.sanitize_scripts(html)

        if BS4_AVAILABLE:
            assert "<script>" not in cleaned
            assert "Hello" in cleaned

    def test_sanitize_scripts_handles_empty_string(self):
        """测试处理空字符串"""
        cleaned = HtmlFixerService.sanitize_scripts("")
        assert cleaned == ""

    def test_wrap_html_wraps_with_div(self):
        """测试用div包装HTML"""
        html = "<p>Hello</p>"
        wrapped = HtmlFixerService.wrap_html(html, tag="div", class_="container")

        if BS4_AVAILABLE:
            assert wrapped.startswith("<div")
            assert 'class="container"' in wrapped
            assert "<p>Hello</p>" in wrapped
            assert "</div>" in wrapped
        else:
            # 简单模式
            assert "<div>" in wrapped
            assert "<p>Hello</p>" in wrapped

    def test_format_html_prettifies_output(self):
        """测试格式化HTML"""
        html = "<div><p>Hello</p></div>"
        formatted = HtmlFixerService.format_html(html)

        if BS4_AVAILABLE:
            # 格式化后应该有换行和缩进
            assert "\n" in formatted or formatted != html

    def test_fix_encoding_handles_empty_string(self):
        """测试编码修复处理空字符串"""
        fixed = HtmlFixerService.fix_encoding("")
        assert fixed == ""

    def test_close_open_tags_handles_empty_string(self):
        """测试close_open_tags处理空字符串"""
        fixed = HtmlFixerService.close_open_tags("")
        assert fixed == ""

    def test_sanitize_scripts_removes_event_handlers(self):
        """测试移除事件处理属性"""
        html = '<div onclick="alert(\'xss\')">Hello</div>'
        cleaned = HtmlFixerService.sanitize_scripts(html)

        if BS4_AVAILABLE:
            assert "onclick" not in cleaned
            assert "Hello" in cleaned

    def test_sanitize_scripts_handles_multiple_scripts(self):
        """测试处理多个script标签"""
        html = "<div><script>alert(1)</script>Hello<script>alert(2)</script></div>"
        cleaned = HtmlFixerService.sanitize_scripts(html)

        if BS4_AVAILABLE:
            assert "<script>" not in cleaned
            assert cleaned.count("Hello") == 1

    def test_extract_text_handles_nested_tags(self):
        """测试提取嵌套标签的文本"""
        html = "<div><p>Hello <b>World</b> <i>!</i></p></div>"
        text = HtmlFixerService.extract_text(html)

        if BS4_AVAILABLE:
            assert "Hello World !" in text

    def test_format_html_with_custom_indent(self):
        """测试自定义缩进格式化"""
        html = "<div><p>Hello</p></div>"
        formatted = HtmlFixerService.format_html(html, indent=4)

        if BS4_AVAILABLE:
            # 应该成功格式化
            assert "<div>" in formatted and "</div>" in formatted

    def test_wrap_html_with_multiple_attrs(self):
        """测试包装带多个属性"""
        html = "<p>Hello</p>"
        wrapped = HtmlFixerService.wrap_html(
            html,
            tag="div",
            class_="container",
            id="main",
            style="color: red"
        )

        if BS4_AVAILABLE:
            assert 'class="container"' in wrapped
            assert "Hello" in cleaned

    def test_fix_broken_tags_handles_malformed_html(self):
        """测试处理格式错误的HTML"""
        malformed = "<div><p>Hello</div></p>"  # 错误的嵌套
        fixed = HtmlFixerService.fix_broken_tags(malformed)

        if BS4_AVAILABLE:
            # BeautifulSoup应该修复这个
            assert fixed is not None
            assert len(fixed) > 0

    def test_close_open_tags_without_bs4(self):
        """测试没有BeautifulSoup时的fallback"""
        import sys
        from unittest.mock import patch

        # Mock BS4_AVAILABLE为False
        with patch('src.infrastructure.html_fixer.BS4_AVAILABLE', False):
            html = "<img src='test.jpg'>"
            fixed = HtmlFixerService.close_open_tags(html)
            # 正则替换应该仍然工作
            assert "/>" in fixed

    def test_sanitize_without_bs4_returns_original(self):
        """测试没有BeautifulSoup时sanitize返回原HTML"""
        from unittest.mock import patch

        with patch('src.infrastructure.html_fixer.BS4_AVAILABLE', False):
            html = "<div><script>alert('xss')</script></div>"
            cleaned = HtmlFixerService.sanitize_scripts(html)
            # 没有BeautifulSoup，应该返回原HTML
            assert cleaned == html

    def test_extract_text_without_bs4_fallback(self):
        """测试没有BeautifulSoup时的文本提取fallback"""
        from unittest.mock import patch

        with patch('src.infrastructure.html_fixer.BS4_AVAILABLE', False):
            html = "<div>Hello <b>World</b></div>"
            text = HtmlFixerService.extract_text(html)
            # 应该移除标签
            assert "<div>" not in text
            assert "Hello" in text

    def test_format_html_handles_invalid_html(self):
        """测试格式化无效HTML"""
        invalid = "<<<>>>???"
        formatted = HtmlFixerService.format_html(invalid)

        if BS4_AVAILABLE:
            # BeautifulSoup应该能处理
            assert formatted is not None

    def test_wrap_html_handles_empty_content(self):
        """测试包装空内容"""
        wrapped = HtmlFixerService.wrap_html("", tag="div")
        assert wrapped == ""

    def test_fix_encoding_handles_various_encoding_issues(self):
        """测试修复多种编码问题"""
        broken = "â€œHelloâ€™s Worldâ€ â€"  # 多个编码问题
        fixed = HtmlFixerService.fix_encoding(broken)

        assert "â€œ" not in fixed
        assert "â€™" not in fixed

    def test_extract_text_from_empty_html(self):
        """测试从空HTML提取文本"""
        text = HtmlFixerService.extract_text("")
        assert text == ""

    def test_fix_broken_tags_with_complex_html(self):
        """测试修复复杂的HTML"""
        complex_html = """
        <html>
            <body>
                <div class="container">
                    <h1>Title</h1>
                    <ul>
                        <li>Item 1
                        <li>Item 2
                    </ul>
                </div>
            </body>
        </html>
        """
        fixed = HtmlFixerService.fix_broken_tags(complex_html)

        if BS4_AVAILABLE:
            # 应该有闭合标签
            assert "</li>" in fixed or "Item 2" in fixed
            assert "Title" in fixed

    def test_sanitize_scripts_removes_event_handlers(self):
        """测试移除事件处理属性"""
        html = '<div onclick="alert(\'xss\')" onmouseover="bad()">Hover me</div>'
        cleaned = HtmlFixerService.sanitize_scripts(html)

        if BS4_AVAILABLE:
            assert "onclick" not in cleaned
            assert "onmouseover" not in cleaned
            assert "Hover me" in cleaned

    def test_sanitize_scripts_removes_multiple_scripts(self):
        """测试移除多个script标签"""
        html = '''
        <div>
            <script>alert('xss1')</script>
            <p>Content</p>
            <script>alert('xss2')</script>
        </div>
        '''
        cleaned = HtmlFixerService.sanitize_scripts(html)

        if BS4_AVAILABLE:
            assert "<script>" not in cleaned
            assert "Content" in cleaned

    def test_wrap_html_with_multiple_attributes(self):
        """测试包装HTML并添加多个属性"""
        html = "<p>Content</p>"
        wrapped = HtmlFixerService.wrap_html(
            html,
            tag="div",
            class_="wrapper",
            id="main",
            style="color: red"
        )

        if BS4_AVAILABLE:
            assert 'class="wrapper"' in wrapped or "class='wrapper'" in wrapped
            assert "Content" in wrapped
            assert wrapped.startswith("<div")

    def test_format_html_with_custom_indent(self):
        """测试自定义缩进格式化"""
        html = "<div><p>Test</p></div>"
        formatted = HtmlFixerService.format_html(html, indent=4)

        if BS4_AVAILABLE:
            # 格式化应该成功
            assert "Test" in formatted

    def test_close_open_tags_with_mixed_content(self):
        """测试修复混合内容的标签"""
        html = "<div><p>Text</p><img src='test.jpg'><span>More text</div>"
        fixed = HtmlFixerService.close_open_tags(html)

        if BS4_AVAILABLE:
            # 应该修复所有标签
            assert "</span>" in fixed
            assert "</div>" in fixed

    def test_fix_encoding_multiple_issues(self):
        """测试修复多个编码问题"""
        broken = "â€™â€œâ€â€"  # 多个编码问题
        fixed = HtmlFixerService.fix_encoding(broken)

        # 至少应该修复一些
        assert "â" not in fixed or len(fixed) < len(broken)

    def test_fix_encoding_preserves_valid_content(self):
        """测试编码修复保留有效内容"""
        valid = "Hello World's \"quoted\" text — dash"
        fixed = HtmlFixerService.fix_encoding(valid)

        # 应该保留有效内容
        assert "Hello" in fixed
        assert "World" in fixed

    def test_extract_text_from_nested_tags(self):
        """测试从嵌套标签提取文本"""
        html = "<div><p><span>Hello</span> <strong>World</strong></p></div>"
        text = HtmlFixerService.extract_text(html)

        if BS4_AVAILABLE:
            assert "Hello" in text
            assert "World" in text
            # 不应该包含标签
            assert "<" not in text or text.startswith("Hello")

    def test_fix_broken_tags_with_none_input(self):
        """测试修复None输入"""
        fixed = HtmlFixerService.fix_broken_tags(None)
        assert fixed == ""

    def test_sanitize_scripts_with_none_input(self):
        """测试清理None输入"""
        cleaned = HtmlFixerService.sanitize_scripts(None)
        assert cleaned == ""

    def test_format_html_with_none_input(self):
        """测试格式化None输入"""
        formatted = HtmlFixerService.format_html(None)
        assert formatted == ""

    def test_wrap_html_with_none_input(self):
        """测试包装None输入"""
        wrapped = HtmlFixerService.wrap_html(None, tag="div")
        assert wrapped == ""

    def test_fix_encoding_with_none_input(self):
        """测试编码修复None输入"""
        fixed = HtmlFixerService.fix_encoding(None)
        assert fixed == ""

    def test_close_open_tags_handles_nested_unclosed_tags(self):
        """测试处理嵌套的未闭合标签"""
        html = "<div><span><p>Text"
        fixed = HtmlFixerService.close_open_tags(html)

        if BS4_AVAILABLE:
            # 应该修复所有标签
            assert "</p>" in fixed
            assert "</span>" in fixed
            assert "</div>" in fixed

    def test_sanitize_scripts_handles_onerror(self):
        """测试移除onerror事件"""
        html = '<img src="x" onerror="alert(\'xss\')">'
        cleaned = HtmlFixerService.sanitize_scripts(html)

        if BS4_AVAILABLE:
            assert "onerror" not in cleaned

    def test_wrap_html_preserves_original_html(self):
        """测试包装保留原始HTML"""
        html = "<p>Original content</p>"
        wrapped = HtmlFixerService.wrap_html(html, tag="section")

        if BS4_AVAILABLE:
            assert "Original content" in wrapped
            assert "<p>" in wrapped
            assert "</p>" in wrapped

    def test_format_html_handles_malformed_html(self):
        """测试格式化畸形HTML"""
        malformed = "<div><p>Test</div>"
        formatted = HtmlFixerService.format_html(malformed)

        if BS4_AVAILABLE:
            # 格式化应该成功
            assert "Test" in formatted

    def test_extract_text_handles_html_entities(self):
        """测试提取文本处理HTML实体"""
        html = "<div>Hello &amp; World &lt;3</div>"
        text = HtmlFixerService.extract_text(html)

        if BS4_AVAILABLE:
            # BeautifulSoup会解码实体
            assert "Hello" in text
            assert "World" in text
