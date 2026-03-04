# -*- coding: utf-8 -*-
"""工具服务：加载和管理工具配置"""
import yaml
import logging
import time
from pathlib import Path
from typing import List, Optional, Dict
from ..models import Tool

logger = logging.getLogger(__name__)


class ToolService:
    """工具加载和管理服务"""
    
    def __init__(self, config_dir: str = "configs/tools", config_loader=None):
        """
        初始化工具服务
        
        Args:
            config_dir: 工具配置文件目录路径（相对于项目根目录）
            config_loader: 配置加载器实例（用于加载系统提示词文件）
        """
        self.config_dir = Path(config_dir)
        self.config_loader = config_loader
        self._tools_cache: Optional[List[Tool]] = None
        self._cache_timestamp: Optional[float] = None
    
    def load_tool(self, config_path: Path, toolset_id: Optional[str] = None) -> Optional[Tool]:
        """
        从配置文件加载单个工具
        
        Args:
            config_path: 配置文件路径
            toolset_id: 工具集ID（用于从文件加载系统提示词）
            
        Returns:
            Tool 实例，如果加载失败返回 None
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 读取 system_prompt（可能为 None）
            system_prompt = config_data.get('system_prompt')
            system_prompt_file = config_data.get('system_prompt_file')
            
            # 如果指定了 system_prompt_file，从文件加载
            if system_prompt_file and self.config_loader and toolset_id:
                loaded_prompt = self.config_loader.load_system_prompt_from_file(
                    toolset_id=toolset_id,
                    prompt_file=system_prompt_file
                )
                if loaded_prompt:
                    system_prompt = loaded_prompt
                else:
                    logger.warning(f"无法从文件加载系统提示词: {system_prompt_file}，工具: {config_data.get('tool_id')}")
            
            # 确定 toolset_id（从配置读取，或从路径推断）
            tool_toolset_id = config_data.get('toolset_id')
            if not tool_toolset_id and toolset_id:
                tool_toolset_id = toolset_id
            if not tool_toolset_id:
                tool_toolset_id = 'ai_tools'  # 默认值（向后兼容）
            
            # 构建 Tool
            tool = Tool(
                tool_id=config_data.get('tool_id', ''),
                name=config_data.get('name', ''),
                description=config_data.get('description'),
                system_prompt=system_prompt,
                category=config_data.get('category', ''),
                icon=config_data.get('icon'),
                visible=config_data.get('visible', True),  # 默认值为 True
                type=config_data.get('type', 'normal'),  # 默认值为 'normal'
                welcome_message=config_data.get('welcome_message', ''),
                order=config_data.get('order', 999),  # 默认值为 999
                toolset_id=tool_toolset_id,
                system_prompt_file=system_prompt_file,
                model=config_data.get('model'),  # 新增：AI模型配置
                content_type=config_data.get('content_type', 'text'),  # 新增：内容类型，默认text
                media_type=config_data.get('media_type')  # 新增：媒体类型
            )
            
            # 验证配置
            if not tool.validate():
                return None
            
            return tool
            
        except Exception as e:
            # 加载失败，静默返回 None（根据业务规则，失败的工具不包含在列表中）
            logger.warning(f"加载工具配置失败: {config_path}, 错误: {e}")
            return None
    
    def load_tools_from_directory(self, directory: Path, toolset_id: str) -> List[Tool]:
        """
        从指定目录加载工具（支持新的目录结构）
        
        Args:
            directory: 工具配置目录
            toolset_id: 工具集ID
            
        Returns:
            工具列表
        """
        tools = []
        
        if not directory.exists():
            return tools
        
        # 扫描所有 .yaml 文件（不递归子目录）
        for config_file in directory.glob("*.yaml"):
            # 跳过特殊文件
            if config_file.name in ['categories.yaml', 'navigation.yaml']:
                continue
            tool = self.load_tool(config_file, toolset_id=toolset_id)
            if tool and tool.visible:  # 只返回 visible=true 的工具
                tools.append(tool)
        
        # 也支持 .yml 扩展名
        for config_file in directory.glob("*.yml"):
            if config_file.name in ['categories.yml', 'navigation.yml']:
                continue
            tool = self.load_tool(config_file, toolset_id=toolset_id)
            if tool and tool.visible:  # 只返回 visible=true 的工具
                tools.append(tool)
        
        return tools
    
    def load_all_tools(self) -> List[Tool]:
        """
        加载所有配置的工具（带缓存机制）
        只返回 visible=true 的工具
        支持新的目录结构（configs/tools/{toolset_id}/）和旧的扁平结构
        
        Returns:
            工具列表（只包含成功加载且 visible=true 的工具）
        """
        # 检查缓存是否有效（5分钟过期）
        current_time = time.time()
        if (self._tools_cache is not None and 
            self._cache_timestamp is not None and 
            current_time - self._cache_timestamp < 300):
            return self._tools_cache
        
        tools = []
        
        if not self.config_dir.exists():
            self._tools_cache = tools
            self._cache_timestamp = current_time
            return tools
        
        # 检查是否是新的目录结构（有子目录）
        has_subdirs = any(item.is_dir() for item in self.config_dir.iterdir())
        
        if has_subdirs:
            # 新的目录结构：扫描每个工具集子目录
            for toolset_dir in self.config_dir.iterdir():
                if toolset_dir.is_dir():
                    toolset_id = toolset_dir.name
                    toolset_tools = self.load_tools_from_directory(toolset_dir, toolset_id)
                    tools.extend(toolset_tools)
        else:
            # 旧的扁平结构（向后兼容）
            for config_file in self.config_dir.glob("*.yaml"):
                if config_file.name != 'categories.yaml':
                    tool = self.load_tool(config_file, toolset_id='ai_tools')
                    if tool and tool.visible:
                        tools.append(tool)
            
            for config_file in self.config_dir.glob("*.yml"):
                if config_file.name != 'categories.yml':
                    tool = self.load_tool(config_file, toolset_id='ai_tools')
                    if tool and tool.visible:
                        tools.append(tool)
        
        # 更新缓存
        self._tools_cache = tools
        self._cache_timestamp = current_time
        
        return tools
    
    def load_tools_by_toolset(self, toolset_id: str) -> List[Tool]:
        """
        加载指定工具集的工具
        
        Args:
            toolset_id: 工具集ID
            
        Returns:
            工具列表（只包含 visible=true 的工具）
        """
        # 尝试从工具集目录加载
        toolset_dir = self.config_dir / toolset_id
        if toolset_dir.exists() and toolset_dir.is_dir():
            return self.load_tools_from_directory(toolset_dir, toolset_id)
        
        # 如果目录不存在，从缓存中过滤
        all_tools = self.load_all_tools()
        return [tool for tool in all_tools if tool.toolset_id == toolset_id]
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Tool]:
        """
        根据 tool_id 获取指定的工具
        
        Args:
            tool_id: 工具唯一标识符
            
        Returns:
            Tool 实例，如果不存在返回 None
        """
        tools = self.load_all_tools()
        return next((t for t in tools if t.tool_id == tool_id), None)
    
    def load_category_config(self, toolset_id: Optional[str] = None) -> Dict[str, Dict]:
        """
        加载分类配置文件
        
        Args:
            toolset_id: 工具集ID（如果指定，从对应工具集目录加载）
            
        Returns:
            分类配置字典，key 为分类名称，value 包含 order 和 icon
        """
        # 确定配置文件路径
        if toolset_id:
            category_config_path = self.config_dir / toolset_id / "categories.yaml"
        else:
            category_config_path = self.config_dir / "categories.yaml"
        
        category_config: Dict[str, Dict] = {}
        
        if category_config_path.exists():
            try:
                with open(category_config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                
                if config_data and 'categories' in config_data:
                    for cat in config_data['categories']:
                        category_name = cat.get('name', '')
                        if category_name:
                            category_config[category_name] = {
                                'order': cat.get('order', 999),
                                'icon': cat.get('icon')
                            }
            except Exception as e:
                logger.warning(f"加载分类配置失败: {category_config_path}, 错误: {e}")
        
        return category_config
    
    def group_by_category(self, tools: List[Tool], toolset_id: Optional[str] = None) -> List[Dict]:
        """
        按 category 聚合工具，生成分类结构，并按配置的顺序排序
        
        Args:
            tools: 工具列表
            toolset_id: 工具集ID（用于加载对应的分类配置）
            
        Returns:
            分类列表，每个分类包含 name、icon（可选）、order、tools（已排序）
        """
        # 加载分类配置
        category_config = self.load_category_config(toolset_id)
        
        # 使用字典按 category 分组
        category_dict: Dict[str, Dict] = {}
        
        for tool in tools:
            category_name = tool.category
            if category_name not in category_dict:
                # 创建新分类
                cat_config = category_config.get(category_name, {})
                category_dict[category_name] = {
                    'name': category_name,
                    'icon': cat_config.get('icon') or tool.icon,  # 优先使用配置的图标
                    'order': cat_config.get('order', 999),  # 从配置获取，默认999
                    'tools': []
                }
            
            # 添加工具到分类
            category_dict[category_name]['tools'].append(tool)
        
        # 对每个分类内的工具按 order 排序
        for category in category_dict.values():
            category['tools'].sort(key=lambda t: t.order)
        
        # 转换为列表并按 order 排序
        categories = list(category_dict.values())
        categories.sort(key=lambda c: c['order'])
        
        return categories

