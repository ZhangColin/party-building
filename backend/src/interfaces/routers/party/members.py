# -*- coding: utf-8 -*-
"""党员管理API路由"""
import logging
from typing import List, Optional, Annotated

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session

from ....models_party import (
    PartyMemberCreate,
    PartyMemberUpdate,
    PartyMemberDetail,
    PartyMemberListResponse
)
from ....services.party_member_service import PartyMemberService
from ....database import get_db
from ....interfaces.auth import get_current_user
from ....models import UserInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/party/members", tags=["党员管理"])


# ==================== 依赖注入 ====================

def get_party_member_service(db: Annotated[Session, Depends(get_db)]) -> PartyMemberService:
    """获取党员服务实例（依赖注入）

    Args:
        db: 数据库会话

    Returns:
        PartyMemberService: 党员服务实例
    """
    return PartyMemberService(db)


# ==================== API 端点 ====================

@router.post("", response_model=PartyMemberDetail, status_code=status.HTTP_201_CREATED)
async def create_member(
    member_data: PartyMemberCreate,
    service: Annotated[PartyMemberService, Depends(get_party_member_service)] = None
):
    """创建党员档案

    Args:
        member_data: 创建党员请求数据
        service: 党员服务（依赖注入）

    Returns:
        PartyMemberDetail: 创建的党员详情

    Raises:
        HTTPException: 业务逻辑错误（400）、数据冲突（409）
    """
    try:
        member = await service.create_member(member_data)
        return member
    except ValueError as e:
        # 业务规则错误（如身份证号重复）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建党员档案失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建党员档案失败"
        )


@router.get("", response_model=PartyMemberListResponse)
async def list_members(
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    name: Optional[str] = Query(None, description="姓名（模糊查询）"),
    party_branch: Optional[str] = Query(None, description="党支部"),
    member_type: Optional[str] = Query(None, description="党员类型"),
    status_filter: Optional[str] = Query(None, description="状态", alias="status"),
    service: Annotated[PartyMemberService, Depends(get_party_member_service)] = None
):
    """获取党员列表（支持筛选和分页）

    Args:
        page: 页码（从1开始）
        page_size: 每页数量（1-100）
        name: 姓名筛选（模糊查询）
        party_branch: 党支部筛选（精确匹配）
        member_type: 党员类型筛选（精确匹配）
        status_filter: 状态筛选（精确匹配）
        service: 党员服务（依赖注入）

    Returns:
        PartyMemberListResponse: 党员列表响应

    Raises:
        HTTPException: 服务器内部错误（500）
    """
    try:
        # 使用 status_filter 避免 Query 参数名冲突
        response = await service.list_members(
            page=page,
            page_size=page_size,
            name=name,
            party_branch=party_branch,
            member_type=member_type,
            status=status_filter
        )
        return response
    except Exception as e:
        logger.error(f"获取党员列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取党员列表失败"
        )


@router.get("/{member_id}", response_model=PartyMemberDetail)
async def get_member(
    member_id: str,
    service: Annotated[PartyMemberService, Depends(get_party_member_service)] = None
):
    """获取党员详情

    Args:
        member_id: 党员ID
        service: 党员服务（依赖注入）

    Returns:
        PartyMemberDetail: 党员详情

    Raises:
        HTTPException: 党员不存在（404）、服务器内部错误（500）
    """
    try:
        member = await service.get_member(member_id)
        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="党员不存在"
            )
        return member
    except HTTPException:
        # 重新抛出 404 错误
        raise
    except Exception as e:
        logger.error(f"获取党员详情失败 (ID: {member_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取党员详情失败"
        )


@router.patch("/{member_id}", response_model=PartyMemberDetail)
async def update_member(
    member_id: str,
    member_data: PartyMemberUpdate,
    service: Annotated[PartyMemberService, Depends(get_party_member_service)] = None
):
    """更新党员档案（部分更新）

    Args:
        member_id: 党员ID
        member_data: 更新党员请求数据
        service: 党员服务（依赖注入）

    Returns:
        PartyMemberDetail: 更新后的党员详情

    Raises:
        HTTPException: 党员不存在（404）、业务逻辑错误（400）、服务器内部错误（500）
    """
    try:
        member = await service.update_member(member_id, member_data)
        if member is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="党员不存在"
            )
        return member
    except ValueError as e:
        # 业务规则错误（如身份证号冲突）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        # 重新抛出 404 错误
        raise
    except Exception as e:
        logger.error(f"更新党员档案失败 (ID: {member_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新党员档案失败"
        )


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: str,
    service: Annotated[PartyMemberService, Depends(get_party_member_service)] = None
):
    """删除党员档案（软删除）

    将党员状态更新为"停止党籍"，不会物理删除数据

    Args:
        member_id: 党员ID
        service: 党员服务（依赖注入）

    Returns:
        None: 204 No Content

    Raises:
        HTTPException: 党员不存在（404）、服务器内部错误（500）
    """
    try:
        success = await service.delete_member(member_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="党员不存在"
            )
        return None
    except HTTPException:
        # 重新抛出 404 错误
        raise
    except Exception as e:
        logger.error(f"删除党员档案失败 (ID: {member_id}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除党员档案失败"
        )


@router.post("/batch-import", response_model=dict)
async def batch_import_members(
    members_data: List[PartyMemberCreate],
    service: Annotated[PartyMemberService, Depends(get_party_member_service)] = None
):
    """批量导入党员

    Args:
        members_data: 党员数据列表
        service: 党员服务（依赖注入）

    Returns:
        dict: 批量导入结果，包含成功数量和错误列表
            {
                "success_count": int,  # 成功导入数量
                "total_count": int,    # 总数量
                "errors": List[str]    # 失败原因列表
            }

    Raises:
        HTTPException: 服务器内部错误（500）
    """
    try:
        success_count, errors = await service.batch_import_members(members_data)

        return {
            "success_count": success_count,
            "total_count": len(members_data),
            "errors": errors
        }
    except Exception as e:
        logger.error(f"批量导入党员失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量导入党员失败"
        )
