# -*- coding: utf-8 -*-
"""Interfaces layer dependency injection

This module provides dependency functions for FastAPI routes in the interfaces layer.
It bridges the new DDD structure with existing services.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import HTTPException, status, Depends
from src.routers.dependencies import (
    get_tool_service,
    get_ai_service,
    get_session_service,
    get_artifact_parser,
    get_title_generator,
    get_auth_service,
    get_user_service,
    get_config_loader,
    get_conversion_service,
    get_common_tool_service,
    get_work_service,
    get_course_service,
)
from src.interfaces.auth import get_current_user
from src.models import UserInfo
from typing import Annotated

# Export all dependencies for use in interfaces layer routes
__all__ = [
    "get_tool_service",
    "get_ai_service",
    "get_session_service",
    "get_artifact_parser",
    "get_title_generator",
    "get_auth_service",
    "get_user_service",
    "get_config_loader",
    "get_conversion_service",
    "get_common_tool_service",
    "get_work_service",
    "get_course_service",
    "get_current_user",
    "require_admin",  # 新增
]


async def require_admin(current_user: Annotated[UserInfo, Depends(get_current_user)]) -> UserInfo:
    """
    管理员权限验证（依赖注入函数）

    Args:
        current_user: 当前登录用户

    Returns:
        UserInfo: 当前用户信息（已验证为管理员）

    Raises:
        HTTPException: 用户不是管理员
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )

    return current_user
