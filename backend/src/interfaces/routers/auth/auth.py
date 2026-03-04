# -*- coding: utf-8 -*-
"""认证路由

从旧架构（routers/auth.py）迁移到DDD架构（interfaces/routers/auth/auth.py）
包含用户登录、获取当前用户信息等接口。
"""
import re
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from src.models import LoginRequest, LoginResponse, UserInfo, UserInfoResponse
from src.interfaces.dependencies import get_auth_service, get_user_service
from src.interfaces.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录（支持用户名、邮箱或手机号）"""
    user_service = get_user_service()
    auth_service = get_auth_service()

    # 判断账号类型：手机号 > 邮箱 > 用户名（优先级）
    phone_pattern = r'^1[3-9]\d{9}$'
    email_pattern = r'^[^@]+@[^@]+\.[^@]+$'

    user = None
    if re.match(phone_pattern, request.account):
        # 手机号登录（优先级最高）
        user = user_service.get_user_by_phone(request.account)
    elif re.match(email_pattern, request.account):
        # 邮箱登录
        user = user_service.get_user_by_email(request.account)
    else:
        # 用户名登录（默认）
        user = user_service.get_user_by_username(request.account)

    # 验证用户是否存在和密码是否正确
    if user is None or not user.verify_password(request.password):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    # 生成JWT Token
    token = auth_service.generate_token(user, remember_me=request.remember_me)

    # 计算Token有效期（秒）
    expires_in = 604800 if request.remember_me else 86400  # 7天或24小时

    # 构建用户信息（不包含密码）
    user_info = UserInfo(
        user_id=user.user_id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        is_admin=user.is_admin
    )

    return LoginResponse(
        token=token,
        user=user_info,
        expires_in=expires_in
    )


@router.get("/me", response_model=UserInfoResponse)
async def get_me(current_user: Annotated[UserInfo, Depends(get_current_user)]):
    """获取当前登录用户信息"""
    return UserInfoResponse(user=current_user)
