# -*- coding: utf-8 -*-
"""
HTML修复服务

统一处理HTML标签修复、清理和格式化
"""
import re
from typing import List
import logging

logger = logging.getLogger(__name__)

# BeautifulSoup 可选导入
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.warning("BeautifulSoup4 未安装，部分 HTML 修复功能将不可用")


class HtmlFixerService:
    """
    HTML修复服务

    提供HTML标签修复、XSS防护、格式化等功能
    """

    @staticmethod
    def fix_broken_tags(html: str) -> str:
        """
        修复未闭合的HTML标签

        使用BeautifulSoup确保所有标签正确闭合

        Args:
            html: 原始HTML字符串

        Returns:
            str: 修复后的HTML字符串
        """
        if not html:
            return ""

        if not BS4_AVAILABLE:
            logger.warning("BeautifulSoup4 未安装，无法修复 HTML 标签")
            return html

        try:
            soup = BeautifulSoup(html, 'lxml')
            return str(soup)
        except Exception as e:
            logger.error(f"HTML fix error: {e}")
            return html

    @staticmethod
    def close_open_tags(html: str) -> str:
        """
        关闭未闭合的标签（正则表达式方法）

        主要用于简单场景的快速修复

        Args:
            html: 原始HTML字符串

        Returns:
            str: 修复后的HTML字符串
        """
        if not html:
            return ""

        # 修复自闭合标签
        html = re.sub(r'<(img|br|hr)([^>]*)(?<!/)\s*>', r'<\1\2 />', html)

        if not BS4_AVAILABLE:
            logger.warning("BeautifulSoup4 未安装，只能做基础标签修复")
            return html

        # 使用BeautifulSoup确保所有标签闭合
        soup = BeautifulSoup(html, 'lxml')
        return soup.prettify()

    @staticmethod
    def sanitize_scripts(html: str) -> str:
        """
        移除危险的script标签和事件处理属性

        Args:
            html: 原始HTML字符串

        Returns:
            str: 清理后的HTML字符串
        """
        if not html:
            return ""

        if not BS4_AVAILABLE:
            logger.warning("BeautifulSoup4 未安装，无法清理 HTML")
            return html

        try:
            soup = BeautifulSoup(html, 'lxml')

            # 移除所有script标签
            for script in soup.find_all('script'):
                script.decompose()

            # 移除危险的事件处理属性
            dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover']
            for tag in soup.find_all(True):
                for attr in dangerous_attrs:
                    if tag.has_attr(attr):
                        del tag[attr]

            return str(soup)

        except Exception as e:
            logger.error(f"HTML sanitize error: {e}")
            return html

    @staticmethod
    def extract_text(html: str) -> str:
        """
        从HTML中提取纯文本

        Args:
            html: HTML字符串

        Returns:
            str: 纯文本内容
        """
        if not html:
            return ""

        if not BS4_AVAILABLE:
            # 简单的文本提取（移除标签）
            return re.sub(r'<[^>]+>', '', html)

        try:
            soup = BeautifulSoup(html, 'lxml')
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            logger.error(f"HTML text extraction error: {e}")
            return html

    @staticmethod
    def format_html(html: str, indent: int = 2) -> str:
        """
        格式化HTML代码

        Args:
            html: 原始HTML字符串
            indent: 缩进空格数

        Returns:
            str: 格式化后的HTML字符串
        """
        if not html:
            return ""

        if not BS4_AVAILABLE:
            logger.warning("BeautifulSoup4 未安装，无法格式化 HTML")
            return html

        try:
            soup = BeautifulSoup(html, 'lxml')
            return soup.prettify(indentator=' ' * indent)
        except Exception as e:
            logger.error(f"HTML format error: {e}")
            return html

    @staticmethod
    def wrap_html(html: str, tag: str = "div", **attrs) -> str:
        """
        用指定标签包装HTML

        Args:
            html: 原始HTML字符串
            tag: 包装标签名
            **attrs: 标签属性

        Returns:
            str: 包装后的HTML字符串
        """
        if not html:
            return ""

        if not BS4_AVAILABLE:
            # 简单包装（不处理属性）
            return f'<{tag}>{html}</{tag}>'

        try:
            soup = BeautifulSoup(html, 'lxml')
            wrapper = soup.new_tag(tag, **attrs)
            wrapper.append(soup)
            return str(wrapper)
        except Exception as e:
            logger.error(f"HTML wrap error: {e}")
            return html

    @staticmethod
    def fix_encoding(html: str) -> str:
        """
        修复HTML编码问题

        Args:
            html: 原始HTML字符串

        Returns:
            str: 修复编码后的HTML字符串
        """
        if not html:
            return ""

        try:
            # 修复常见的编码问题
            html = html.replace('â€™', "'")
            html = html.replace('â€œ', '"')
            html = html.replace('â€\x9d', '"')
            html = html.replace('â€', '—')

            return html
        except Exception as e:
            logger.error(f"HTML encoding fix error: {e}")
            return html
