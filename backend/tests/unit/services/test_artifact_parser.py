# -*- coding: utf-8 -*-
"""ArtifactParser 单元测试"""
import pytest
from src.services.artifact_parser import ArtifactParser


class TestArtifactParser:
    """ArtifactParser 测试类"""

    # ==================== detect_language_by_content 测试 ====================

    def test_detect_html_by_tag(self):
        """测试通过 HTML 标签识别"""
        content = "<html><body>Hello</body></html>"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "html"

    def test_detect_html_by_div(self):
        """测试通过 div 标签识别 HTML"""
        content = "<div>Content</div>"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "html"

    def test_detect_html_by_script(self):
        """测试通过 script 标签识别 HTML"""
        content = "<script>console.log('test');</script>"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "html"

    def test_detect_svg_by_tag(self):
        """测试通过 svg 标签识别 SVG"""
        content = "<svg><circle cx='50' cy='50' r='40'/></svg>"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "svg"

    def test_detect_svg_by_path(self):
        """测试通过 path 标签识别 SVG"""
        content = "<path d='M10 20 L30 40' />"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "svg"

    def test_detect_markdown_by_heading(self):
        """测试通过 # 标题识别 Markdown"""
        content = "# Heading 1\n\nSome content"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "markdown"

    def test_detect_markdown_by_list(self):
        """测试通过列表识别 Markdown"""
        content = "- Item 1\n- Item 2\n- Item 3"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "markdown"

    def test_detect_markdown_by_bold(self):
        """测试通过粗体识别 Markdown"""
        content = "This is **bold** text"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "markdown"

    def test_detect_markdown_by_link(self):
        """测试通过链接识别 Markdown"""
        content = "[Link text](https://example.com)"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "markdown"

    def test_detect_markdown_by_code(self):
        """测试通过代码块识别 Markdown"""
        content = "`inline code`"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "markdown"

    def test_detect_text_default(self):
        """测试默认识别为 text"""
        content = "Plain text without any special markers"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "text"

    def test_detect_html_case_insensitive(self):
        """测试 HTML 标签检测不区分大小写"""
        content = "<HTML><BODY>Hello</BODY></HTML>"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "html"

    def test_detect_svg_case_insensitive(self):
        """测试 SVG 标签检测不区分大小写"""
        content = "<SVG><PATH d='M10 20'/></SVG>"
        result = ArtifactParser.detect_language_by_content(content)
        assert result == "svg"

    # ==================== parse_from_markdown 测试 ====================

    def test_parse_html_artifact(self):
        """测试解析 HTML 成果物"""
        content = '''
以下是生成的 HTML 课件：

```html
<html>
  <body>
    <h1>Hello</h1>
  </body>
</html>
```
'''
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 1
        assert artifacts[0].type == "html"
        assert artifacts[0].language == "html"
        assert "<html>" in artifacts[0].content

    def test_parse_svg_artifact(self):
        """测试解析 SVG 成果物"""
        content = '生成的 SVG 图表：\n```svg\n<svg><circle cx="50" cy="50" r="40"/></svg>\n```'
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 1
        assert artifacts[0].type == "svg"
        assert artifacts[0].language == "svg"
        assert "<svg>" in artifacts[0].content

    def test_parse_markdown_artifact(self):
        """测试解析 Markdown 成果物"""
        content = '```markdown\n# Heading\n\nContent\n```'
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 1
        assert artifacts[0].type == "markdown"
        assert "# Heading" in artifacts[0].content

    def test_parse_multiple_artifacts(self):
        """测试解析多个成果物"""
        content = '''
HTML: ```html\n<html></html>\n```
SVG: ```svg\n<svg></svg>\n```
'''
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 2
        assert artifacts[0].type == "html"
        assert artifacts[1].type == "svg"

    def test_parse_no_artifact(self):
        """测试无成果物"""
        content = "这是一段普通文本，没有代码块"
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 0

    def test_parse_empty_string(self):
        """测试解析空字符串"""
        artifacts = ArtifactParser.parse_from_markdown("")

        assert len(artifacts) == 0

    def test_parse_artifact_without_language(self):
        """测试解析没有语言标识的代码块（自动检测）"""
        content = '```\n<div>Content</div>\n```'
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 1
        # 应该自动检测为 html
        assert artifacts[0].type == "html"

    def test_parse_xml_as_svg(self):
        """测试 XML 声明但内容是 SVG，应识别为 SVG"""
        content = '```xml\n<svg><circle cx="50" cy="50" r="40"/></svg>\n```'
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 1
        # XML 声明但内容是 SVG，应识别为 svg
        assert artifacts[0].type == "svg"
        assert artifacts[0].language == "svg"

    def test_parse_xml_not_svg(self):
        """测试 XML 声明且内容不是 SVG，保持为 xml"""
        content = '```xml\n<root><item>test</item></root>\n```'
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 1
        assert artifacts[0].type == "xml"
        assert artifacts[0].language == "xml"

    def test_parse_artifact_content_stripped(self):
        """测试代码内容被正确去除首尾空白"""
        content = '```html\n\n  <html>\n  </html>\n\n  ```'
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 1
        # 内容应该被 strip
        assert artifacts[0].content.startswith("<html>")
        assert artifacts[0].content.endswith("</html>")

    def test_parse_multiline_code_block(self):
        """测试多行代码块解析"""
        content = '''
```html
<html>
  <head><title>Test</title></head>
  <body>
    <h1>Heading</h1>
    <p>Paragraph</p>
  </body>
</html>
```
'''
        artifacts = ArtifactParser.parse_from_markdown(content)

        assert len(artifacts) == 1
        assert "<html>" in artifacts[0].content
        assert "</html>" in artifacts[0].content
