# -*- coding: utf-8 -*-
"""测试配置加载器"""
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from src.config_loader import ConfigLoader
from src.models import NavigationModule


class TestConfigLoader:
    """测试ConfigLoader"""

    def test_init_with_default_config_root(self):
        """测试使用默认配置根目录初始化"""
        loader = ConfigLoader()
        assert loader.config_root == Path("configs")
        assert loader._navigation_cache is None
        assert loader._prompt_cache == {}

    def test_init_with_custom_config_root(self):
        """测试使用自定义配置根目录初始化"""
        loader = ConfigLoader(config_root="custom_configs")
        assert loader.config_root == Path("custom_configs")

    def test_load_navigation_when_file_not_exists(self):
        """测试导航配置文件不存在时返回默认配置"""
        loader = ConfigLoader(config_root="nonexistent_configs")

        modules = loader.load_navigation()

        assert len(modules) == 1
        assert modules[0].name == "AI工具"
        assert modules[0].type == "toolset"
        assert modules[0].config_source == "tools/ai_tools"
        assert modules[0].icon == "🤖"
        assert modules[0].order == 1

    @patch("builtins.open", new_callable=mock_open, read_data="")
    @patch("pathlib.Path.exists")
    def test_load_navigation_with_empty_file(self, mock_exists, mock_file):
        """测试空导航配置文件"""
        mock_exists.return_value = True
        loader = ConfigLoader()

        modules = loader.load_navigation()

        assert modules == []

    @patch("builtins.open", new_callable=mock_open, read_data="modules: []")
    @patch("pathlib.Path.exists")
    def test_load_navigation_with_empty_modules(self, mock_exists, mock_file):
        """测试空的模块列表"""
        mock_exists.return_value = True
        loader = ConfigLoader()

        modules = loader.load_navigation()

        assert modules == []

    @patch("builtins.open", new_callable=mock_open, read_data="""
modules:
  - name: AI工具
    type: toolset
    config_source: tools/ai_tools
    icon: 🤖
    order: 1

  - name: 通用工具
    type: page
    page_path: /common-tools
    icon: 🔧
    order: 2
""")
    @patch("pathlib.Path.exists")
    def test_load_navigation_success(self, mock_exists, mock_file):
        """测试成功加载导航配置"""
        mock_exists.return_value = True
        loader = ConfigLoader()

        modules = loader.load_navigation()

        assert len(modules) == 2
        assert modules[0].name == "AI工具"
        assert modules[0].type == "toolset"
        assert modules[0].config_source == "tools/ai_tools"
        assert modules[0].order == 1

        assert modules[1].name == "通用工具"
        assert modules[1].type == "page"
        assert modules[1].page_path == "/common-tools"
        assert modules[1].order == 2

    @patch("builtins.open", new_callable=mock_open, read_data="""
modules:
  - name: 第二个
    type: toolset
    config_source: tools/tool2
    order: 2

  - name: 第一个
    type: toolset
    config_source: tools/tool1
    order: 1
""")
    @patch("pathlib.Path.exists")
    def test_load_navigation_sorts_by_order(self, mock_exists, mock_file):
        """测试按order排序"""
        mock_exists.return_value = True
        loader = ConfigLoader()

        modules = loader.load_navigation()

        assert len(modules) == 2
        assert modules[0].name == "第一个"
        assert modules[1].name == "第二个"

    @patch("builtins.open", new_callable=mock_open, read_data="""
modules:
  - name: 无排序
    type: toolset
    config_source: tools/tool1
""")
    @patch("pathlib.Path.exists")
    def test_load_navigation_uses_default_order(self, mock_exists, mock_file):
        """测试使用默认order值"""
        mock_exists.return_value = True
        loader = ConfigLoader()

        modules = loader.load_navigation()

        assert len(modules) == 1
        assert modules[0].order == 999

    @patch("builtins.open", new_callable=mock_open, read_data="""
modules:
  - name: 有效模块
    type: toolset
    config_source: tools/tool1
    order: 1

  - name: 无效模块
    type: toolset
    # 缺少 config_source

  - name: 另一个有效模块
    type: toolset
    config_source: tools/tool2
    order: 2
""")
    @patch("pathlib.Path.exists")
    def test_load_navigation_skips_invalid_modules(self, mock_exists, mock_file):
        """测试跳过无效的模块配置"""
        mock_exists.return_value = True
        loader = ConfigLoader()

        modules = loader.load_navigation()

        assert len(modules) == 2
        assert modules[0].name == "有效模块"
        assert modules[1].name == "另一个有效模块"

    @patch("builtins.open", new_callable=mock_open, read_data="""
modules:
  - name: AI工具
    type: toolset
    config_source: tools/ai_tools
    order: 1
""")
    @patch("pathlib.Path.exists")
    def test_load_navigation_uses_cache(self, mock_exists, mock_file):
        """测试使用缓存"""
        mock_exists.return_value = True
        loader = ConfigLoader()

        # 第一次加载
        modules1 = loader.load_navigation()
        # 第二次加载（应该使用缓存）
        modules2 = loader.load_navigation()

        assert len(modules1) == 1
        assert len(modules2) == 1
        # open应该只被调用一次（使用缓存）
        assert mock_file.call_count == 1

    def test_clear_cache(self):
        """测试清除缓存"""
        loader = ConfigLoader(config_root="nonexistent_configs")

        # 加载默认配置（会有缓存）
        modules1 = loader.load_navigation()
        assert loader._navigation_cache is not None

        # 清除缓存
        loader.clear_cache()
        assert loader._navigation_cache is None
        assert loader._prompt_cache == {}

    @patch("builtins.open", new_callable=mock_open, read_data="test prompt content")
    @patch("pathlib.Path.exists")
    def test_load_system_prompt_from_file_success(self, mock_exists, mock_file):
        """测试成功加载系统提示词"""
        mock_exists.return_value = True
        loader = ConfigLoader()

        content = loader.load_system_prompt_from_file("ai_tools", "prompts/teacher.md")

        assert content == "test prompt content"

    @patch("pathlib.Path.exists")
    def test_load_system_prompt_from_file_not_exists(self, mock_exists):
        """测试系统提示词文件不存在"""
        mock_exists.return_value = False
        loader = ConfigLoader()

        content = loader.load_system_prompt_from_file("ai_tools", "prompts/teacher.md")

        assert content is None

    @patch("builtins.open", new_callable=mock_open, read_data="test prompt")
    @patch("pathlib.Path.exists")
    def test_load_system_prompt_uses_cache(self, mock_exists, mock_file):
        """测试系统提示词使用缓存"""
        mock_exists.return_value = True
        loader = ConfigLoader()

        # 第一次加载
        content1 = loader.load_system_prompt_from_file("ai_tools", "prompts/teacher.md")
        # 第二次加载（应该使用缓存）
        content2 = loader.load_system_prompt_from_file("ai_tools", "prompts/teacher.md")

        assert content1 == "test prompt"
        assert content2 == "test prompt"
        # open应该只被调用一次（使用缓存）
        assert mock_file.call_count == 1
