# -*- coding: utf-8 -*-
"""认证依赖模块（供interfaces层使用）

此模块提供认证相关的依赖注入函数，与routers层解耦。
"""
import logging
from typing import Annotated

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.models import UserInfo

logger = logging.getLogger(__name__)

# 全局共享的 security 实例
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> UserInfo:
    """
    获取当前登录用户（依赖注入函数）

    Args:
        credentials: HTTP Bearer Token凭证

    Returns:
        UserInfo: 当前用户信息

    Raises:
        HTTPException: Token无效、过期或用户不存在
    """
    # 导入服务（避免循环导入）
    from src.routers.dependencies import get_auth_service, get_user_service

    token = credentials.credentials

    # 验证Token并获取用户ID
    auth_service = get_auth_service()
    user_id = auth_service.get_user_id_from_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 根据用户ID查询用户
    user_service = get_user_service()
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 返回用户信息（不包含密码）
    return UserInfo(
        user_id=user.user_id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        is_admin=user.is_admin
    )


__all__ = ["security", "get_current_user"]
