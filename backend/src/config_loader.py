# -*- coding: utf-8 -*-
"""配置加载器：加载导航配置和系统提示词文件"""
import yaml
import logging
from pathlib import Path
from typing import List, Optional, Dict
from .models import NavigationModule

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器：负责加载导航配置和系统提示词文件"""
    
    def __init__(self, config_root: str = "configs"):
        """
        初始化配置加载器
        
        Args:
            config_root: 配置文件根目录路径（相对于项目根目录）
        """
        self.config_root = Path(config_root)
        self._navigation_cache: Optional[List[NavigationModule]] = None
        self._prompt_cache: Dict[str, str] = {}  # key: file_path, value: content
    
    def load_navigation(self) -> List[NavigationModule]:
        """
        加载导航配置文件（navigation.yaml）
        
        Returns:
            导航模块列表（已排序）
        """
        # 检查缓存
        if self._navigation_cache is not None:
            return self._navigation_cache
        
        navigation_file = self.config_root / "navigation.yaml"
        
        # 如果配置文件不存在，返回默认配置（向后兼容）
        if not navigation_file.exists():
            logger.warning(f"导航配置文件不存在: {navigation_file}，使用默认配置")
            default_module = NavigationModule(
                name="AI工具",
                type="toolset",
                config_source="tools/ai_tools",
                icon="🤖",
                order=1
            )
            self._navigation_cache = [default_module]
            return self._navigation_cache
        
        try:
            with open(navigation_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data or 'modules' not in config_data:
                logger.error(f"导航配置文件格式错误: {navigation_file}")
                return []
            
            modules = []
            for module_data in config_data['modules']:
                try:
                    module = NavigationModule(
                        name=module_data.get('name', ''),
                        type=module_data.get('type', 'toolset'),
                        config_source=module_data.get('config_source'),
                        page_path=module_data.get('page_path'),
                        icon=module_data.get('icon'),
                        order=module_data.get('order', 999)
                    )
                    
                    # 验证配置
                    if module.validate():
                        modules.append(module)
                    else:
                        logger.warning(f"无效的导航模块配置: {module_data}")
                        
                except Exception as e:
                    logger.warning(f"加载导航模块失败: {module_data}, 错误: {e}")
                    continue
            
            # 按 order 排序
            modules.sort(key=lambda m: m.order)
            
            # 缓存
            self._navigation_cache = modules
            return modules
            
        except Exception as e:
            logger.error(f"加载导航配置失败: {navigation_file}, 错误: {e}", exc_info=True)
            return []
    
    def load_system_prompt_from_file(self, toolset_id: str, prompt_file: str) -> Optional[str]:
        """
        从文件加载系统提示词
        
        Args:
            toolset_id: 工具集ID（如 "ai_tools"）
            prompt_file: 提示词文件路径（相对于工具集配置目录，如 "prompts/teacher.md"）
            
        Returns:
            系统提示词内容，如果加载失败返回 None
        """
        # 构建完整文件路径
        file_path = self.config_root / "tools" / toolset_id / prompt_file
        
        # 规范化路径（用于缓存key）
        cache_key = str(file_path.resolve())
        
        # 检查缓存
        if cache_key in self._prompt_cache:
            return self._prompt_cache[cache_key]
        
        # 检查文件是否存在
        if not file_path.exists():
            logger.error(f"系统提示词文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 缓存
            self._prompt_cache[cache_key] = content
            return content
            
        except Exception as e:
            logger.error(f"加载系统提示词文件失败: {file_path}, 错误: {e}", exc_info=True)
            return None
    
    def clear_cache(self):
        """清除所有缓存"""
        self._navigation_cache = None
        self._prompt_cache.clear()
