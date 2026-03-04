"""Agent 服务：加载和管理 Agent 配置"""
import yaml
import logging
import time
from pathlib import Path
from typing import List, Optional
from ..models import Agent, UIConfig

logger = logging.getLogger(__name__)


class AgentService:
    """Agent 加载和管理服务"""
    
    def __init__(self, config_dir: str = "configs/agents"):
        """
        初始化 Agent 服务
        
        Args:
            config_dir: Agent 配置文件目录路径（相对于项目根目录）
        """
        self.config_dir = Path(config_dir)
        self._agents_cache: Optional[List[Agent]] = None
        self._cache_timestamp: Optional[float] = None
    
    def load_agent(self, config_path: Path) -> Optional[Agent]:
        """
        从配置文件加载单个 Agent
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Agent 实例，如果加载失败返回 None
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 构建 UIConfig
            ui_config_data = config_data.get('ui_config', {})
            ui_config = UIConfig(
                show_preview=ui_config_data.get('show_preview', False),
                preview_types=ui_config_data.get('preview_types', [])
            )
            
            # 构建 Agent
            agent = Agent(
                agent_id=config_data.get('agent_id', ''),
                name=config_data.get('name', ''),
                description=config_data.get('description'),
                system_prompt=config_data.get('system_prompt', ''),
                ui_config=ui_config,
                capabilities=config_data.get('capabilities', [])
            )
            
            # 验证配置
            if not agent.validate():
                return None
            
            return agent
            
        except Exception as e:
            # 加载失败，静默返回 None（根据业务规则，失败的 Agent 不包含在列表中）
            logger.warning(f"加载 Agent 配置失败: {config_path}, 错误: {e}")
            return None
    
    def load_all_agents(self) -> List[Agent]:
        """
        加载所有配置的 Agent（带缓存机制）
        
        Returns:
            Agent 列表（只包含成功加载的 Agent）
        """
        # 检查缓存是否有效（5分钟过期）
        current_time = time.time()
        if (self._agents_cache is not None and 
            self._cache_timestamp is not None and 
            current_time - self._cache_timestamp < 300):
            return self._agents_cache
        
        agents = []
        
        if not self.config_dir.exists():
            self._agents_cache = agents
            self._cache_timestamp = current_time
            return agents
        
        # 扫描所有 .yaml 文件
        for config_file in self.config_dir.glob("*.yaml"):
            agent = self.load_agent(config_file)
            if agent:
                agents.append(agent)
        
        # 也支持 .yml 扩展名
        for config_file in self.config_dir.glob("*.yml"):
            agent = self.load_agent(config_file)
            if agent:
                agents.append(agent)
        
        # 更新缓存
        self._agents_cache = agents
        self._cache_timestamp = current_time
        
        return agents
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """
        根据 agent_id 获取指定的 Agent
        
        Args:
            agent_id: Agent 唯一标识符
            
        Returns:
            Agent 实例，如果不存在返回 None
        """
        agents = self.load_all_agents()
        return next((a for a in agents if a.agent_id == agent_id), None)

