# -*- coding: utf-8 -*-
"""用户管理路由

提供用户列表、创建用户、更新用户、删除用户、重置密码等管理员接口。
"""
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, status, Depends

from src.models import (
    UserInfo,
    UserListResponse,
    UserListItem,
    CreateUserRequest,
    CreateUserResponse,
    UpdateUserRequest,
    UpdateUserResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from src.interfaces.dependencies import get_user_service
from src.interfaces.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/users", tags=["用户管理"])


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


@router.get("", response_model=UserListResponse)
async def get_user_list(
    page: int = 1,
    page_size: int = 20,
    is_admin: Optional[bool] = None,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """获取用户列表（管理员功能）- 支持分页和筛选"""
    # 限制每页最大数量
    if page_size > 100:
        page_size = 100

    user_service = get_user_service()
    users, total = user_service.get_all_users(
        page=page,
        page_size=page_size,
        is_admin=is_admin
    )

    # 转换为API响应格式
    user_items = [
        UserListItem(
            user_id=user.user_id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            is_admin=user.is_admin,
            created_at=user.created_at
        )
        for user in users
    ]

    return UserListResponse(
        users=user_items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", response_model=CreateUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """创建新用户（管理员功能）"""
    try:
        user_service = get_user_service()
        user = user_service.create_user(
            username=request.username,
            nickname=request.nickname,
            email=request.email,
            password=request.password,
            phone=request.phone,
            avatar=request.avatar,
            is_admin=request.is_admin
        )

        # 转换为API响应格式
        user_item = UserListItem(
            user_id=user.user_id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            is_admin=user.is_admin,
            created_at=user.created_at
        )

        return CreateUserResponse(user=user_item)
    except ValueError as e:
        # 用户名、邮箱或手机号已存在
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/{user_id}", response_model=UpdateUserResponse)
async def get_user(
    user_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """获取单个用户信息（管理员功能）"""
    user_service = get_user_service()
    user = user_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 转换为API响应格式
    user_item = UserListItem(
        user_id=user.user_id,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        phone=user.phone,
        avatar=user.avatar,
        is_admin=user.is_admin,
        created_at=user.created_at
    )

    return UpdateUserResponse(user=user_item)


@router.put("/{user_id}", response_model=UpdateUserResponse)
async def update_user_put(
    user_id: str,
    request: UpdateUserRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """
    更新用户信息（管理员功能）- PUT方法（完整替换）

    PUT方法用于完整替换资源，与PATCH方法功能相同
    因为UpdateUserRequest已经处理了部分更新逻辑
    """
    return await _update_user_impl(user_id, request, current_user)


@router.patch("/{user_id}", response_model=UpdateUserResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """更新用户信息（管理员功能）- PATCH方法（部分更新）"""
    return await _update_user_impl(user_id, request, current_user)


async def _update_user_impl(
    user_id: str,
    request: UpdateUserRequest,
    current_user: UserInfo,
) -> UpdateUserResponse:
    """
    更新用户的实现逻辑

    Args:
        user_id: 用户ID
        request: 更新请求（包含可选字段）
        current_user: 当前管理员用户

    Returns:
        UpdateUserResponse: 更新后的用户信息

    Raises:
        HTTPException: 用户不存在、业务规则错误、冲突等
    """
    try:
        user_service = get_user_service()
        user = user_service.update_user(
            user_id=user_id,
            username=request.username,
            nickname=request.nickname,
            email=request.email,
            phone=request.phone,
            is_admin=request.is_admin
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 转换为API响应格式
        user_item = UserListItem(
            user_id=user.user_id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            phone=user.phone,
            avatar=user.avatar,
            is_admin=user.is_admin,
            created_at=user.created_at
        )

        return UpdateUserResponse(user=user_item)
    except ValueError as e:
        # 业务规则错误（如取消最后一个管理员、用户名/邮箱/手机号冲突）
        if "最后一个管理员" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """删除用户（管理员功能）"""
    try:
        user_service = get_user_service()
        success = user_service.delete_user(user_id, current_user_id=current_user.user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        return None  # 204 No Content
    except ValueError as e:
        # 业务规则错误（如删除自己、删除最后一个管理员）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{user_id}/reset-password", response_model=ResetPasswordResponse)
async def reset_user_password(
    user_id: str,
    request: ResetPasswordRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """重置用户密码（管理员功能）"""
    try:
        user_service = get_user_service()
        success = user_service.reset_password(user_id, request.new_password)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        return ResetPasswordResponse(
            message="密码已重置",
            new_password=request.new_password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
