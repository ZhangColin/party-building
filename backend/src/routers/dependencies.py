# -*- coding: utf-8 -*-
"""服务依赖注入模块

管理所有服务的初始化和依赖注入，确保服务使用正确的配置路径。
"""
import sys
import os
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv

# 加载环境变量（必须在导入服务之前执行）
load_dotenv()

# 获取项目根目录
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config_loader import ConfigLoader
from src.services.agent_service import AgentService
from src.services.tool_service import ToolService
from src.services.session_service import SessionService
from src.services.ai_service import AIService
from src.services.artifact_parser import ArtifactParser
from src.services.user_service import UserService
from src.services.auth_service import AuthService
from src.services.conversion_service import ConversionService
from src.services.common_tool_service import CommonToolService
from src.services.work_service import WorkService
from src.services.course_service import CourseService
from src.services.title_generator import TitleGenerator


@lru_cache
def get_config_loader() -> ConfigLoader:
    """获取配置加载器实例（单例）"""
    return ConfigLoader(config_root=str(project_root / "configs"))


@lru_cache
def get_agent_service() -> AgentService:
    """获取 Agent 服务实例（单例）"""
    return AgentService(config_dir=str(project_root / "configs" / "agents"))


@lru_cache
def get_tool_service() -> ToolService:
    """获取 Tool 服务实例（单例）"""
    return ToolService(
        config_dir=str(project_root / "configs" / "tools"),
        config_loader=get_config_loader()
    )


@lru_cache
def get_session_service() -> SessionService:
    """获取 Session 服务实例（单例）"""
    return SessionService()


@lru_cache
def get_ai_service() -> AIService:
    """获取 AI 服务实例（单例）"""
    return AIService()


@lru_cache
def get_artifact_parser() -> ArtifactParser:
    """获取 Artifact 解析器实例（单例）"""
    return ArtifactParser()


@lru_cache
def get_user_service() -> UserService:
    """获取 User 服务实例（单例）"""
    return UserService()


@lru_cache
def get_auth_service() -> AuthService:
    """获取 Auth 服务实例（单例）"""
    return AuthService()


@lru_cache
def get_conversion_service() -> ConversionService:
    """获取 Conversion 服务实例（单例）"""
    return ConversionService()


@lru_cache
def get_common_tool_service() -> CommonToolService:
    """获取 CommonTool 服务实例（单例）"""
    return CommonToolService()


@lru_cache
def get_work_service() -> WorkService:
    """获取 Work 服务实例（单例）"""
    return WorkService()


@lru_cache
def get_course_service() -> CourseService:
    """获取 Course 服务实例（单例）"""
    return CourseService()


@lru_cache
def get_title_generator() -> TitleGenerator:
    """获取标题生成器实例（单例）"""
    return TitleGenerator()
