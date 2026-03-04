"""成果物解析服务：从 Markdown 中提取代码块"""
import re
from datetime import datetime
from typing import List
from ..models import Artifact


class ArtifactParser:
    """成果物解析服务"""
    
    # Markdown 代码块正则表达式
    CODE_BLOCK_PATTERN = re.compile(
        r'```(\w+)?\n(.*?)```',
        re.DOTALL  # 允许 . 匹配换行符
    )
    
    @staticmethod
    def detect_language_by_content(content: str) -> str:
        """
        根据内容特征智能识别代码块类型
        
        识别规则（按优先级）：
        1. HTML：包含 HTML 标签（<html>, <div>, <script>, <style> 等）
        2. SVG：包含 SVG 标签（<svg>, <path>, <circle>, <rect> 等）
        3. Markdown：包含 Markdown 特征（# 标题、- 列表、**粗体**、[]() 链接等）
        4. 默认：text
        
        Args:
            content: 代码块内容
            
        Returns:
            识别出的语言类型
        """
        content_lower = content.lower().strip()
        
        # HTML 特征检测
        html_tags = ['<html', '<div', '<script', '<style', '<body', '<head', 
                     '<title', '<meta', '<link', '<button', '<input', '<form']
        if any(tag in content_lower for tag in html_tags):
            return 'html'
        
        # SVG 特征检测
        svg_tags = ['<svg', '<path', '<circle', '<rect', '<line', '<polygon',
                    '<polyline', '<ellipse', '<text', '<g ', '<defs', '<use']
        if any(tag in content_lower for tag in svg_tags):
            return 'svg'
        
        # Markdown 特征检测
        # 1. 标题：以 # 开头（可能有空格）
        if re.search(r'^#+\s+', content, re.MULTILINE):
            return 'markdown'
        
        # 2. 列表：以 - 或 * 开头（可能有空格）
        if re.search(r'^[\s]*[-*+]\s+', content, re.MULTILINE):
            return 'markdown'
        
        # 3. 粗体/斜体：包含 ** 或 * 或 __ 或 _
        if re.search(r'\*\*.*?\*\*|__.*?__|\*.*?\*|_.*?_', content):
            return 'markdown'
        
        # 4. 链接：包含 [text](url) 格式
        if re.search(r'\[.*?\]\(.*?\)', content):
            return 'markdown'
        
        # 5. 代码块：包含 `代码` 或 ```代码块```
        if re.search(r'`[^`]+`|```', content):
            return 'markdown'
        
        # 默认返回 text
        return 'text'
    
    @staticmethod
    def parse_from_markdown(content: str) -> List[Artifact]:
        """
        从 Markdown 文本中提取代码块，生成成果物列表
        
        Args:
            content: Markdown 文本内容
            
        Returns:
            成果物列表
        """
        artifacts = []
        matches = ArtifactParser.CODE_BLOCK_PATTERN.findall(content)
        
        for language, code_content in matches:
            # 代码内容去除首尾空白
            code_content = code_content.strip()
            
            # 处理语言标识
            if language:
                # 有显式声明，使用声明的类型
                language = language.strip()
                # 但是，如果声明的是 'xml' 但内容是 SVG，应该识别为 'svg'
                if language.lower() == 'xml':
                    detected = ArtifactParser.detect_language_by_content(code_content)
                    if detected == 'svg':
                        language = 'svg'
            else:
                # 没有显式声明，使用智能识别
                language = ArtifactParser.detect_language_by_content(code_content)
            
            # 确定成果物类型（由语言标识决定）
            artifact_type = language
            
            # 创建 Artifact 对象
            artifact = Artifact(
                type=artifact_type,
                content=code_content,
                language=language,
                timestamp=datetime.now()
            )
            artifacts.append(artifact)
        
        return artifacts

