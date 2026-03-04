# -*- coding: utf-8 -*-
"""
会话管理路由

提供会话列表、会话详情、会话删除等接口
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from src.models import ConversationListResponse, Message, UserInfo
from src.interfaces.dependencies import get_session_service, get_current_user
from src.services.session_service import SessionService
from typing import Annotated, List

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/tools/{tool_id}/conversations", response_model=ConversationListResponse, tags=["会话"])
async def get_conversations(
    tool_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    session_service: SessionService = Depends(get_session_service)
):
    """
    获取用户在指定工具下的会话列表

    返回按时间倒序排列的会话列表
    """
    try:
        sessions = session_service.get_sessions_by_user_and_tool(
            user_id=current_user.user_id,
            tool_id=tool_id
        )

        # 转换为API响应格式
        conversation_items = [
            {
                "session_id": s.session_id,
                "title": s.title,
                "updated_at": s.updated_at
            }
            for s in sessions
        ]

        return ConversationListResponse(conversations=conversation_items)

    except Exception as e:
        logger.error(f"Get conversations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tools/{tool_id}/conversations/{conv_id}", tags=["会话"])
async def delete_conversation(
    tool_id: str,
    conv_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    session_service: SessionService = Depends(get_session_service)
):
    """
    删除指定会话

    同时删除会话下的所有消息和成果物
    """
    try:
        # 验证会话存在
        session = session_service.get_session_by_id(conv_id, current_user.user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # 验证会话属于当前用户且属于指定工具
        if session.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        if session.tool_id != tool_id:
            raise HTTPException(status_code=400, detail="Conversation does not belong to specified tool")

        # 删除会话
        success = session_service.delete_session(conv_id, current_user.user_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete conversation")

        return {"message": "Conversation deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/{tool_id}/conversations/{conv_id}", tags=["会话"])
async def get_conversation(
    tool_id: str,
    conv_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    session_service: SessionService = Depends(get_session_service)
):
    """
    获取会话详情（包含消息历史）
    """
    try:
        # 获取会话
        session = session_service.get_session_by_id(conv_id, current_user.user_id)
        if not session:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # 验证权限
        if session.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        if session.tool_id != tool_id:
            raise HTTPException(status_code=400, detail="Conversation does not belong to specified tool")

        # 获取消息
        messages = session_service.get_messages_by_session(conv_id, current_user.user_id)

        # 转换为API格式
        message_items = [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]

        return {
            "conversation": {
                "session_id": session.session_id,
                "title": session.title,
                "tool_id": session.tool_id,
                "created_at": session.created_at,
                "updated_at": session.updated_at
            },
            "messages": message_items
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
