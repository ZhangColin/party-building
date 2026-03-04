# -*- coding: utf-8 -*-
"""ToolService 单元测试"""
import pytest
import yaml
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from src.services.tool_service import ToolService
from src.models import Tool


class TestToolService:
    """ToolService 测试类"""

    def setup_method(self):
        """每个测试方法前的设置"""
        self.config_dir = Path("configs/tools")
        self.service = ToolService(config_dir=str(self.config_dir))

    def test_init_default_params(self):
        """测试默认参数初始化"""
        service = ToolService()
        assert service.config_dir == Path("configs/tools")
        assert service.config_loader is None
        assert service._tools_cache is None
        assert service._cache_timestamp is None

    def test_init_custom_params(self):
        """测试自定义参数初始化"""
        custom_loader = MagicMock()
        service = ToolService(
            config_dir="custom/tools",
            config_loader=custom_loader
        )
        assert service.config_dir == Path("custom/tools")
        assert service.config_loader == custom_loader
        assert service._tools_cache is None
        assert service._cache_timestamp is None

    @patch('builtins.open', new_callable=mock_open, read_data='tool_id: test_tool\nname: Test Tool\n')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.models.Tool.validate')
    def test_load_tool_success(self, mock_validate, mock_exists, mock_file):
        """测试成功加载工具配置"""
        mock_exists.return_value = True
        mock_validate.return_value = True
        config_path = Path("test_tool.yaml")

        tool = self.service.load_tool(config_path, toolset_id='ai_tools')

        assert tool is not None
        assert tool.tool_id == 'test_tool'
        assert tool.name == 'Test Tool'

    @patch('builtins.open', new_callable=mock_open, read_data='tool_id: test_tool\nname: Test Tool\nsystem_prompt_file: test.md\n')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.models.Tool.validate')
    def test_load_tool_with_system_prompt_file(self, mock_validate, mock_exists, mock_file):
        """测试从文件加载系统提示词"""
        mock_exists.return_value = True
        mock_validate.return_value = True
        config_path = Path("test_tool.yaml")

        # Mock config_loader
        mock_loader = MagicMock()
        mock_loader.load_system_prompt_from_file.return_value = "Loaded prompt"
        self.service.config_loader = mock_loader

        tool = self.service.load_tool(config_path, toolset_id='ai_tools')

        assert tool is not None
        assert tool.system_prompt == "Loaded prompt"
        mock_loader.load_system_prompt_from_file.assert_called_once_with(
            toolset_id='ai_tools',
            prompt_file='test.md'
        )

    @patch('builtins.open', new_callable=mock_open, read_data='tool_id: test_tool\nname: Test Tool\nsystem_prompt_file: test.md\n')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.models.Tool.validate')
    def test_load_tool_with_system_prompt_file_failure(self, mock_validate, mock_exists, mock_file):
        """测试系统提示词文件加载失败时的降级处理"""
        mock_exists.return_value = True
        mock_validate.return_value = True
        config_path = Path("test_tool.yaml")

        # Mock config_loader 返回 None（加载失败）
        mock_loader = MagicMock()
        mock_loader.load_system_prompt_from_file.return_value = None
        self.service.config_loader = mock_loader

        tool = self.service.load_tool(config_path, toolset_id='ai_tools')

        assert tool is not None
        # 应该使用配置中的 system_prompt（这里是 None）
        assert tool.system_prompt is None

    @patch('builtins.open', new_callable=mock_open, read_data='tool_id: test_tool\nname: Test\n')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.models.Tool.validate')
    def test_load_tool_with_toolset_id_from_config(self, mock_validate, mock_exists, mock_file):
        """测试从参数读取 toolset_id（配置中没有）"""
        mock_exists.return_value = True
        mock_validate.return_value = True
        config_path = Path("test_tool.yaml")

        tool = self.service.load_tool(config_path, toolset_id='fallback')

        assert tool is not None
        assert tool.toolset_id == 'fallback'  # 使用参数传入的值

    @patch('builtins.open', new_callable=mock_open, read_data='tool_id: test_tool\nname: Test\ntoolset_id: custom_toolset\n')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.models.Tool.validate')
    def test_load_tool_with_custom_toolset_id(self, mock_validate, mock_exists, mock_file):
        """测试使用自定义 toolset_id"""
        mock_exists.return_value = True
        mock_validate.return_value = True
        config_path = Path("test_tool.yaml")

        tool = self.service.load_tool(config_path, toolset_id='fallback')

        assert tool is not None
        assert tool.toolset_id == 'custom_toolset'

    @patch('builtins.open', new_callable=mock_open, read_data='tool_id: test_tool\nname: Test\n')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.models.Tool.validate')
    def test_load_tool_without_toolset_id_and_no_param(self, mock_validate, mock_exists, mock_file):
        """测试既没有配置 toolset_id 也没有传入参数时使用默认值"""
        mock_exists.return_value = True
        mock_validate.return_value = True
        config_path = Path("test_tool.yaml")

        tool = self.service.load_tool(config_path, toolset_id=None)

        assert tool is not None
        assert tool.toolset_id == 'ai_tools'  # 默认值

    @patch('builtins.open', new_callable=mock_open, read_data='tool_id: test_tool\nname: Test\n')
    @patch('src.services.tool_service.Path.exists')
    def test_load_tool_validation_failure(self, mock_exists, mock_file):
        """测试工具验证失败时返回 None"""
        mock_exists.return_value = True
        config_path = Path("test_tool.yaml")

        # Mock validate 返回 False
        with patch.object(Tool, 'validate', return_value=False):
            tool = self.service.load_tool(config_path, toolset_id='ai_tools')
            assert tool is None

    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('src.services.tool_service.Path.exists')
    def test_load_tool_file_not_found(self, mock_exists, mock_file):
        """测试文件不存在时返回 None"""
        mock_exists.return_value = True
        config_path = Path("nonexistent.yaml")

        tool = self.service.load_tool(config_path, toolset_id='ai_tools')

        assert tool is None

    @patch('builtins.open', side_effect=Exception("YAML parse error"))
    @patch('src.services.tool_service.Path.exists')
    def test_load_tool_yaml_parse_error(self, mock_exists, mock_file):
        """测试 YAML 解析错误时返回 None"""
        mock_exists.return_value = True
        config_path = Path("invalid.yaml")

        tool = self.service.load_tool(config_path, toolset_id='ai_tools')

        assert tool is None

    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.glob')
    def test_load_tools_from_directory_not_exists(self, mock_glob, mock_exists):
        """测试目录不存在时返回空列表"""
        mock_exists.return_value = False
        directory = Path("nonexistent")

        tools = self.service.load_tools_from_directory(directory, 'ai_tools')

        assert tools == []
        mock_glob.assert_not_called()

    @patch('src.services.tool_service.ToolService.load_tool')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.glob')
    def test_load_tools_from_directory_yaml_files(self, mock_glob, mock_exists, mock_load_tool):
        """测试从目录加载 yaml 工具"""
        mock_exists.return_value = True

        # Mock 文件列表
        mock_file1 = MagicMock()
        mock_file1.name = 'tool1.yaml'
        mock_file2 = MagicMock()
        mock_file2.name = 'categories.yaml'  # 应该被跳过

        # glob 会被调用两次（yaml 和 yml）
        mock_glob.side_effect = [[mock_file1, mock_file2], []]

        # Mock 加载工具
        mock_tool = MagicMock(spec=Tool)
        mock_tool.visible = True
        mock_load_tool.return_value = mock_tool

        directory = Path("test_dir")
        tools = self.service.load_tools_from_directory(directory, 'ai_tools')

        assert len(tools) == 1
        assert tools[0] == mock_tool

    @patch('src.services.tool_service.ToolService.load_tool')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.glob')
    def test_load_tools_from_directory_yml_files(self, mock_glob, mock_exists, mock_load_tool):
        """测试从目录加载 yml 工具"""
        mock_exists.return_value = True

        # Mock 文件列表
        mock_file1 = MagicMock()
        mock_file1.name = 'tool1.yml'
        mock_file2 = MagicMock()
        mock_file2.name = 'categories.yml'  # 应该被跳过

        # glob 会被调用两次（yaml 和 yml）
        mock_glob.side_effect = [[], [mock_file1, mock_file2]]

        # Mock 加载工具
        mock_tool = MagicMock(spec=Tool)
        mock_tool.visible = True
        mock_load_tool.return_value = mock_tool

        directory = Path("test_dir")
        tools = self.service.load_tools_from_directory(directory, 'ai_tools')

        assert len(tools) == 1

    @patch('src.services.tool_service.ToolService.load_tool')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.glob')
    def test_load_tools_from_directory_skip_invisible(self, mock_glob, mock_exists, mock_load_tool):
        """测试跳过不可见的工具"""
        mock_exists.return_value = True

        mock_file = MagicMock()
        mock_file.name = 'tool1.yaml'
        mock_glob.return_value = [mock_file]

        # Mock 不可见的工具
        mock_tool = MagicMock(spec=Tool)
        mock_tool.visible = False
        mock_load_tool.return_value = mock_tool

        directory = Path("test_dir")
        tools = self.service.load_tools_from_directory(directory, 'ai_tools')

        assert len(tools) == 0

    @patch('src.services.tool_service.Path.exists')
    def test_load_all_tools_config_dir_not_exists(self, mock_exists):
        """测试配置目录不存在时返回空列表并设置缓存"""
        mock_exists.return_value = False

        tools = self.service.load_all_tools()

        assert tools == []
        assert self.service._tools_cache == []
        assert self.service._cache_timestamp is not None

    @patch('src.services.tool_service.time.time')
    @patch('src.services.tool_service.ToolService.load_tools_from_directory')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.is_dir')
    @patch('src.services.tool_service.Path.iterdir')
    def test_load_all_tools_with_cache(self, mock_iterdir, mock_is_dir, mock_exists, mock_load_from_dir, mock_time):
        """测试缓存机制"""
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        # 第一次调用：缓存为空
        mock_time.side_effect = [1000.0, 1001.0]
        mock_toolset_dir = MagicMock()
        mock_toolset_dir.is_dir.return_value = True
        mock_toolset_dir.name = 'ai_tools'
        mock_iterdir.return_value = [mock_toolset_dir]

        mock_tool = MagicMock(spec=Tool)
        mock_tool.visible = True
        mock_load_from_dir.return_value = [mock_tool]

        # 第一次加载
        tools1 = self.service.load_all_tools()
        assert len(tools1) == 1
        assert self.service._tools_cache == tools1

        # 第二次调用：使用缓存（时间在5分钟内）
        mock_time.side_effect = [1001.0, 1300.0]  # 缓存时间 + 当前时间（在5分钟内）
        tools2 = self.service.load_all_tools()
        assert tools2 == tools1
        assert mock_load_from_dir.call_count == 1  # 只调用一次

    @patch('src.services.tool_service.time.time')
    @patch('src.services.tool_service.ToolService.load_tools_from_directory')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.is_dir')
    @patch('src.services.tool_service.Path.iterdir')
    def test_load_all_tools_cache_expired(self, mock_iterdir, mock_is_dir, mock_exists, mock_load_from_dir, mock_time):
        """测试缓存过期后重新加载"""
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        # 第一次调用 load_all_tools
        # time.time() 被调用两次：行141和行180（但使用同一个变量）
        mock_time.side_effect = [1000.0, 1001.0]
        mock_toolset_dir = MagicMock()
        mock_toolset_dir.is_dir.return_value = True
        mock_toolset_dir.name = 'ai_tools'
        mock_iterdir.return_value = [mock_toolset_dir]

        mock_tool = MagicMock(spec=Tool)
        mock_tool.visible = True
        mock_load_from_dir.return_value = [mock_tool]

        tools1 = self.service.load_all_tools()
        assert mock_load_from_dir.call_count == 1

        # 第二次调用：缓存过期（超过5分钟）
        # time.time() 被调用两次：行141（检查）和行180（更新）
        # 第一次返回 1400.0，与缓存时间差为 1400-1001=399 > 300，过期
        # 第二次返回 1401.0，作为新的缓存时间
        mock_time.side_effect = [1400.0, 1401.0]
        mock_load_from_dir.reset_mock()

        tools2 = self.service.load_all_tools()
        assert mock_load_from_dir.call_count == 1  # 重新加载

    @patch('src.services.tool_service.ToolService.load_tools_from_directory')
    @patch('src.services.tool_service.ToolService.load_tool')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.glob')
    @patch('src.services.tool_service.Path.is_dir')
    @patch('src.services.tool_service.Path.iterdir')
    def test_load_all_tools_legacy_structure(self, mock_iterdir, mock_is_dir, mock_glob, mock_exists, mock_load_tool, mock_load_from_dir):
        """测试旧版扁平结构 - yaml 文件"""
        mock_exists.return_value = True
        mock_is_dir.return_value = False  # 没有子目录

        # Mock yaml 文件
        mock_file = MagicMock()
        mock_file.name = 'tool1.yaml'
        # glob 会被调用两次（yaml 和 yml）
        mock_glob.side_effect = [[mock_file], []]

        mock_tool = MagicMock(spec=Tool)
        mock_tool.visible = True
        mock_load_tool.return_value = mock_tool

        tools = self.service.load_all_tools()

        assert len(tools) == 1
        assert mock_load_tool.call_count == 1

    @patch('src.services.tool_service.ToolService.load_tools_from_directory')
    @patch('src.services.tool_service.ToolService.load_tool')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.glob')
    @patch('src.services.tool_service.Path.is_dir')
    @patch('src.services.tool_service.Path.iterdir')
    def test_load_all_tools_legacy_structure_yml(self, mock_iterdir, mock_is_dir, mock_glob, mock_exists, mock_load_tool, mock_load_from_dir):
        """测试旧版扁平结构 - yml 文件"""
        mock_exists.return_value = True
        mock_is_dir.return_value = False  # 没有子目录

        # Mock yml 文件
        mock_file = MagicMock()
        mock_file.name = 'tool1.yml'
        # glob 会被调用两次（yaml 和 yml）
        mock_glob.side_effect = [[], [mock_file]]

        mock_tool = MagicMock(spec=Tool)
        mock_tool.visible = True
        mock_load_tool.return_value = mock_tool

        tools = self.service.load_all_tools()

        assert len(tools) == 1
        assert mock_load_tool.call_count == 1

    @patch('src.services.tool_service.ToolService.load_tools_from_directory')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.is_dir')
    def test_load_tools_by_toolset_from_directory(self, mock_is_dir, mock_exists, mock_load_from_dir):
        """测试从工具集目录加载工具"""
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        mock_tool = MagicMock(spec=Tool)
        mock_load_from_dir.return_value = [mock_tool]

        tools = self.service.load_tools_by_toolset('ai_tools')

        assert len(tools) == 1
        mock_load_from_dir.assert_called_once()

    @patch('src.services.tool_service.ToolService.load_all_tools')
    @patch('src.services.tool_service.Path.exists')
    @patch('src.services.tool_service.Path.is_dir')
    def test_load_tools_by_toolset_from_cache(self, mock_is_dir, mock_exists, mock_load_all):
        """测试工具集目录不存在时从缓存过滤"""
        mock_exists.return_value = False
        mock_is_dir.return_value = False

        mock_tool1 = MagicMock(spec=Tool)
        mock_tool1.toolset_id = 'ai_tools'
        mock_tool2 = MagicMock(spec=Tool)
        mock_tool2.toolset_id = 'other_tools'
        mock_load_all.return_value = [mock_tool1, mock_tool2]

        tools = self.service.load_tools_by_toolset('ai_tools')

        assert len(tools) == 1
        assert tools[0].toolset_id == 'ai_tools'

    @patch('src.services.tool_service.ToolService.load_all_tools')
    def test_get_tool_by_id_found(self, mock_load_all):
        """测试根据ID找到工具"""
        mock_tool1 = MagicMock(spec=Tool)
        mock_tool1.tool_id = 'tool1'
        mock_tool2 = MagicMock(spec=Tool)
        mock_tool2.tool_id = 'tool2'
        mock_load_all.return_value = [mock_tool1, mock_tool2]

        tool = self.service.get_tool_by_id('tool1')

        assert tool is not None
        assert tool.tool_id == 'tool1'

    @patch('src.services.tool_service.ToolService.load_all_tools')
    def test_get_tool_by_id_not_found(self, mock_load_all):
        """测试根据ID找不到工具"""
        mock_tool = MagicMock(spec=Tool)
        mock_tool.tool_id = 'tool1'
        mock_load_all.return_value = [mock_tool]

        tool = self.service.get_tool_by_id('nonexistent')

        assert tool is None

    @patch('src.services.tool_service.Path.exists')
    def test_load_category_config_file_not_exists(self, mock_exists):
        """测试分类配置文件不存在时返回空字典"""
        mock_exists.return_value = False

        config = self.service.load_category_config('ai_tools')

        assert config == {}

    @patch('builtins.open', new_callable=mock_open, read_data='categories:\n- name: cat1\n  order: 1\n  icon: star\n')
    @patch('src.services.tool_service.Path.exists')
    def test_load_category_config_success(self, mock_exists, mock_file):
        """测试成功加载分类配置"""
        mock_exists.return_value = True

        config = self.service.load_category_config('ai_tools')

        assert 'cat1' in config
        assert config['cat1']['order'] == 1
        assert config['cat1']['icon'] == 'star'

    @patch('builtins.open', new_callable=mock_open, read_data='categories:\n- name: cat1\n  order: 1\n')
    @patch('src.services.tool_service.Path.exists')
    def test_load_category_config_without_toolset(self, mock_exists, mock_file):
        """测试不带 toolset_id 加载分类配置"""
        mock_exists.return_value = True

        config = self.service.load_category_config()

        assert 'cat1' in config

    @patch('builtins.open', new_callable=mock_open, read_data='invalid: yaml\n')
    @patch('src.services.tool_service.Path.exists')
    def test_load_category_config_empty_name(self, mock_exists, mock_file):
        """测试分类名称为空时不添加到配置"""
        mock_exists.return_value = True

        config = self.service.load_category_config('ai_tools')

        assert config == {}

    @patch('builtins.open', side_effect=Exception("Read error"))
    @patch('src.services.tool_service.Path.exists')
    def test_load_category_config_read_error(self, mock_exists, mock_file):
        """测试读取错误时返回空字典"""
        mock_exists.return_value = True

        config = self.service.load_category_config('ai_tools')

        assert config == {}

    @patch('src.services.tool_service.ToolService.load_category_config')
    def test_group_by_category_empty_tools(self, mock_load_cat):
        """测试空工具列表"""
        mock_load_cat.return_value = {}

        categories = self.service.group_by_category([], 'ai_tools')

        assert categories == []

    @patch('src.services.tool_service.ToolService.load_category_config')
    def test_group_by_category_single_tool(self, mock_load_cat):
        """测试单个工具分组"""
        mock_load_cat.return_value = {}

        mock_tool = MagicMock(spec=Tool)
        mock_tool.category = 'cat1'
        mock_tool.icon = 'star'
        mock_tool.order = 1

        categories = self.service.group_by_category([mock_tool], 'ai_tools')

        assert len(categories) == 1
        assert categories[0]['name'] == 'cat1'
        assert categories[0]['icon'] == 'star'
        assert len(categories[0]['tools']) == 1

    @patch('src.services.tool_service.ToolService.load_category_config')
    def test_group_by_category_multiple_tools(self, mock_load_cat):
        """测试多个工具分组"""
        mock_load_cat.return_value = {
            'cat1': {'order': 1, 'icon': 'star'},
            'cat2': {'order': 2, 'icon': 'heart'}
        }

        mock_tool1 = MagicMock(spec=Tool)
        mock_tool1.category = 'cat1'
        mock_tool1.icon = 'star'
        mock_tool1.order = 2

        mock_tool2 = MagicMock(spec=Tool)
        mock_tool2.category = 'cat1'
        mock_tool2.icon = 'star'
        mock_tool2.order = 1

        mock_tool3 = MagicMock(spec=Tool)
        mock_tool3.category = 'cat2'
        mock_tool3.icon = 'heart'
        mock_tool3.order = 1

        categories = self.service.group_by_category(
            [mock_tool1, mock_tool2, mock_tool3],
            'ai_tools'
        )

        assert len(categories) == 2
        # 分类按 order 排序
        assert categories[0]['name'] == 'cat1'
        assert categories[1]['name'] == 'cat2'

        # 分类内工具按 order 排序
        assert categories[0]['tools'][0].order == 1
        assert categories[0]['tools'][1].order == 2

    @patch('src.services.tool_service.ToolService.load_category_config')
    def test_group_by_category_without_config(self, mock_load_cat):
        """测试没有分类配置时使用工具图标"""
        mock_load_cat.return_value = {}

        mock_tool = MagicMock(spec=Tool)
        mock_tool.category = 'cat1'
        mock_tool.icon = 'tool-icon'
        mock_tool.order = 1

        categories = self.service.group_by_category([mock_tool], 'ai_tools')

        assert categories[0]['icon'] == 'tool-icon'
        assert categories[0]['order'] == 999  # 默认值

    @patch('src.services.tool_service.ToolService.load_category_config')
    def test_group_by_category_with_config_icon(self, mock_load_cat):
        """测试使用配置中的图标而非工具图标"""
        mock_load_cat.return_value = {
            'cat1': {'order': 1, 'icon': 'config-icon'}
        }

        mock_tool = MagicMock(spec=Tool)
        mock_tool.category = 'cat1'
        mock_tool.icon = 'tool-icon'
        mock_tool.order = 1

        categories = self.service.group_by_category([mock_tool], 'ai_tools')

        assert categories[0]['icon'] == 'config-icon'
