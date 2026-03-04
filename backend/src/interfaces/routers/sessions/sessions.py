# -*- coding: utf-8 -*-
"""
会话管理路由

提供会话详情、更新会话标题、删除会话等接口
"""
import logging
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends

from src.models import (
    UserInfo,
    SessionDetailResponse,
    UpdateSessionRequest,
    UpdateSessionResponse,
    Message,
)
from src.interfaces.dependencies import get_session_service, get_current_user
from src.services.session_service import SessionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["会话管理"])


@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    session_service: SessionService = Depends(get_session_service),
):
    """获取指定会话的完整消息历史"""
    # 获取会话（验证是否属于当前用户）
    session = session_service.get_session_by_id(session_id, user_id=current_user.user_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found"
        )

    # 获取消息列表
    messages = session_service.get_messages_by_session(session_id, user_id=current_user.user_id)
    logger.info(f"获取会话消息 - 会话ID: {session_id}, 消息数量: {len(messages)}")
    for i, msg in enumerate(messages):
        logger.info(f"  消息 {i+1} - 角色: {msg.role}, 时间: {msg.created_at}, 内容前20字: {msg.content[:20]}")

    # 转换为 API 响应格式（设置 timestamp 字段）
    message_list = []
    for msg in messages:
        message_list.append(
            Message(
                message_id=msg.message_id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
                timestamp=msg.timestamp or msg.created_at,
                artifacts=msg.artifacts,
                media_content=msg.media_content  # 添加多模态内容字段
            )
        )

    return SessionDetailResponse(
        session_id=session.session_id,
        tool_id=session.tool_id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=message_list
    )


@router.patch("/sessions/{session_id}", response_model=UpdateSessionResponse)
async def update_session_title(
    session_id: str,
    request: UpdateSessionRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    session_service: SessionService = Depends(get_session_service),
):
    """更新指定会话的标题"""
    # 更新会话标题
    session = session_service.update_session_title(
        session_id=session_id,
        new_title=request.title,
        user_id=current_user.user_id
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found"
        )

    return UpdateSessionResponse(
        session_id=session.session_id,
        title=session.title
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    session_service: SessionService = Depends(get_session_service),
):
    """删除指定会话（级联删除消息和成果物）"""
    success = session_service.delete_session(session_id, user_id=current_user.user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found"
        )

    return {"message": "Session deleted successfully"}


@router.get("/agents/{agent_id}/sessions")
async def get_agent_sessions(
    agent_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
):
    """获取指定代理的所有会话（已废弃，保留兼容性）"""
    # 此接口已废弃，返回空列表
    return {"sessions": []}
