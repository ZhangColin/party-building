# -*- coding: utf-8 -*-
"""AgentService 单元测试"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.services.agent_service import AgentService
from src.models import Agent, UIConfig


class TestAgentService:
    """AgentService 测试类"""

    def test_init_default_config_dir(self):
        """测试初始化 - 默认配置目录"""
        service = AgentService()
        assert service.config_dir == Path("configs/agents")
        assert service._agents_cache is None
        assert service._cache_timestamp is None

    def test_init_custom_config_dir(self):
        """测试初始化 - 自定义配置目录"""
        service = AgentService(config_dir="custom/path")
        assert service.config_dir == Path("custom/path")

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_agent_success(self, mock_yaml, mock_open):
        """测试加载单个 Agent - 成功"""
        mock_yaml.return_value = {
            'agent_id': 'test_agent',
            'name': '测试 Agent',
            'description': '这是一个测试',
            'system_prompt': '你是一个助手',
            'ui_config': {
                'show_preview': True,
                'preview_types': ['html', 'svg']
            },
            'capabilities': ['聊天', '生成']
        }

        service = AgentService()
        agent = service.load_agent(Path("test.yaml"))

        assert agent is not None
        assert agent.agent_id == 'test_agent'
        assert agent.name == '测试 Agent'
        assert agent.description == '这是一个测试'
        assert agent.system_prompt == '你是一个助手'
        assert agent.ui_config.show_preview is True
        assert agent.ui_config.preview_types == ['html', 'svg']
        assert agent.capabilities == ['聊天', '生成']

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_agent_minimal_config(self, mock_yaml, mock_open):
        """测试加载单个 Agent - 最小配置"""
        mock_yaml.return_value = {
            'agent_id': 'minimal',
            'name': '最小配置',
            'system_prompt': '基本提示词',  # 必需字段
            'ui_config': {
                'show_preview': False
            }
        }

        service = AgentService()
        agent = service.load_agent(Path("minimal.yaml"))

        assert agent is not None
        assert agent.agent_id == 'minimal'
        assert agent.name == '最小配置'
        assert agent.description is None
        assert agent.system_prompt == '基本提示词'
        assert agent.ui_config.show_preview is False
        assert agent.ui_config.preview_types == []
        assert agent.capabilities == []

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_agent_invalid_no_id(self, mock_yaml, mock_open):
        """测试加载单个 Agent - 缺少 agent_id"""
        mock_yaml.return_value = {
            'name': '无效 Agent'
        }

        service = AgentService()
        agent = service.load_agent(Path("invalid.yaml"))

        assert agent is None

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_agent_invalid_no_name(self, mock_yaml, mock_open):
        """测试加载单个 Agent - 缺少 name"""
        mock_yaml.return_value = {
            'agent_id': 'test'
        }

        service = AgentService()
        agent = service.load_agent(Path("invalid.yaml"))

        assert agent is None

    @patch("builtins.open")
    def test_load_agent_file_error(self, mock_open):
        """测试加载单个 Agent - 文件读取错误"""
        mock_open.side_effect = IOError("文件不存在")

        service = AgentService()
        agent = service.load_agent(Path("error.yaml"))

        assert agent is None

    @patch("builtins.open")
    @patch("yaml.safe_load")
    def test_load_agent_yaml_error(self, mock_yaml, mock_open):
        """测试加载单个 Agent - YAML 解析错误"""
        mock_yaml.side_effect = Exception("YAML 格式错误")

        service = AgentService()
        agent = service.load_agent(Path("bad.yaml"))

        assert agent is None

    @patch("src.services.agent_service.Path.exists")
    def test_load_all_agents_dir_not_exists(self, mock_exists):
        """测试加载所有 Agent - 目录不存在"""
        mock_exists.return_value = False

        service = AgentService()
        agents = service.load_all_agents()

        assert agents == []
        assert service._agents_cache == []
        assert service._cache_timestamp is not None

    @patch("src.services.agent_service.Path.glob")
    @patch("src.services.agent_service.Path.exists")
    def test_load_all_agents_empty_dir(self, mock_exists, mock_glob):
        """测试加载所有 Agent - 空目录"""
        mock_exists.return_value = True
        mock_glob.return_value = []

        service = AgentService()
        agents = service.load_all_agents()

        assert agents == []
        # glob 被调用了两次（*.yaml 和 *.yml）
        assert mock_glob.call_count == 2

    @patch("src.services.agent_service.AgentService.load_agent")
    @patch("src.services.agent_service.Path.glob")
    @patch("src.services.agent_service.Path.exists")
    def test_load_all_agents_success(self, mock_exists, mock_glob, mock_load):
        """测试加载所有 Agent - 成功加载多个"""
        mock_exists.return_value = True

        # 模拟 .yaml 文件
        mock_glob.side_effect = [
            [Path("agent1.yaml"), Path("agent2.yaml")],  # 第一次调用 *.yaml
            []  # 第二次调用 *.yml
        ]

        # 模拟加载结果
        agent1 = MagicMock()
        agent1.agent_id = "agent1"
        agent2 = MagicMock()
        agent2.agent_id = "agent2"

        mock_load.side_effect = [agent1, agent2]

        service = AgentService()
        agents = service.load_all_agents()

        assert len(agents) == 2
        assert agents[0].agent_id == "agent1"
        assert agents[1].agent_id == "agent2"

    @patch("src.services.agent_service.AgentService.load_agent")
    @patch("src.services.agent_service.Path.glob")
    @patch("src.services.agent_service.Path.exists")
    def test_load_all_agents_with_invalid(self, mock_exists, mock_glob, mock_load):
        """测试加载所有 Agent - 包含无效配置"""
        mock_exists.return_value = True

        mock_glob.side_effect = [
            [Path("valid.yaml"), Path("invalid.yaml")],
            []
        ]

        # 只有第一个有效，第二个返回 None
        valid_agent = MagicMock()
        valid_agent.agent_id = "valid"
        mock_load.side_effect = [valid_agent, None]

        service = AgentService()
        agents = service.load_all_agents()

        assert len(agents) == 1
        assert agents[0].agent_id == "valid"

    @patch("src.services.agent_service.AgentService.load_agent")
    @patch("src.services.agent_service.Path.glob")
    @patch("src.services.agent_service.Path.exists")
    def test_load_all_agents_yml_extension(self, mock_exists, mock_glob, mock_load):
        """测试加载所有 Agent - 支持 .yml 扩展名"""
        mock_exists.return_value = True

        agent_yml = MagicMock()
        agent_yml.agent_id = "yml_agent"

        mock_glob.side_effect = [
            [],  # *.yaml 无文件
            [Path("config.yml")]  # *.yml 有文件
        ]
        mock_load.return_value = agent_yml

        service = AgentService()
        agents = service.load_all_agents()

        assert len(agents) == 1
        assert agents[0].agent_id == "yml_agent"

    @patch("src.services.agent_service.time.time")
    def test_load_all_agents_cache_hit(self, mock_time):
        """测试加载所有 Agent - 缓存命中"""
        # 设置缓存
        service = AgentService()
        cached_agents = [MagicMock(agent_id="cached")]
        service._agents_cache = cached_agents
        service._cache_timestamp = 100.0

        # 模拟当前时间在缓存有效期内（5分钟）
        mock_time.return_value = 200.0  # 差值 100秒 < 300秒

        agents = service.load_all_agents()

        assert agents == cached_agents
        assert len(agents) == 1

    @patch("src.services.agent_service.time.time")
    @patch("src.services.agent_service.Path.exists")
    def test_load_all_agents_cache_expired(self, mock_exists, mock_time):
        """测试加载所有 Agent - 缓存过期"""
        mock_exists.return_value = False

        service = AgentService()
        cached_agents = [MagicMock(agent_id="cached")]
        service._agents_cache = cached_agents
        service._cache_timestamp = 100.0

        # 模拟当前时间超过缓存有效期（5分钟）
        mock_time.return_value = 500.0  # 差值 400秒 > 300秒

        agents = service.load_all_agents()

        # 应该重新加载（虽然目录不存在返回空列表）
        assert agents == []
        assert agents is not cached_agents

    @patch("src.services.agent_service.AgentService.load_agent")
    @patch("src.services.agent_service.Path.glob")
    @patch("src.services.agent_service.Path.exists")
    def test_get_agent_by_id_found(self, mock_exists, mock_glob, mock_load):
        """测试根据 ID 获取 Agent - 找到"""
        mock_exists.return_value = True
        mock_glob.side_effect = [[Path("test.yaml")], []]

        agent = MagicMock()
        agent.agent_id = "target_agent"
        mock_load.return_value = agent

        service = AgentService()
        result = service.get_agent_by_id("target_agent")

        assert result is not None
        assert result.agent_id == "target_agent"

    @patch("src.services.agent_service.AgentService.load_agent")
    @patch("src.services.agent_service.Path.glob")
    @patch("src.services.agent_service.Path.exists")
    def test_get_agent_by_id_not_found(self, mock_exists, mock_glob, mock_load):
        """测试根据 ID 获取 Agent - 未找到"""
        mock_exists.return_value = True
        mock_glob.side_effect = [[Path("test.yaml")], []]

        agent = MagicMock()
        agent.agent_id = "other_agent"
        mock_load.return_value = agent

        service = AgentService()
        result = service.get_agent_by_id("target_agent")

        assert result is None

    @patch("src.services.agent_service.Path.exists")
    def test_get_agent_by_id_empty_agents(self, mock_exists):
        """测试根据 ID 获取 Agent - 空 Agent 列表"""
        mock_exists.return_value = False

        service = AgentService()
        result = service.get_agent_by_id("any_id")

        assert result is None
