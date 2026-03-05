# -*- coding: utf-8 -*-
"""
工具对话路由

提供工具对话接口，支持流式和非流式两种模式
"""
import logging
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from src.models import ChatRequest, ChatResponse, Message, Artifact, UserInfo
from src.interfaces.dependencies import (
    get_ai_service,
    get_session_service,
    get_tool_service,
    get_artifact_parser,
    get_title_generator,
)
from src.services.ai_service import AIService
from src.services.session_service import SessionService
from src.services.tool_service import ToolService
from typing import Annotated
from src.interfaces.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/tools/{tool_id}/chat/stream", tags=["对话"])
async def chat_stream(
    tool_id: str,
    request: ChatRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    ai_service: AIService = Depends(get_ai_service),
    session_service: SessionService = Depends(get_session_service),
    tool_service: ToolService = Depends(get_tool_service),
    title_generator = Depends(get_title_generator),
):
    """
    流式对话接口

    使用Server-Sent Events (SSE)返回AI的流式响应
    """
    # 获取工具配置
    tool = tool_service.get_tool_by_id(tool_id)

    # 调试输出
    logger.info(f"🔍 查找工具: tool_id='{tool_id}'")
    logger.info(f"🔍 找到工具: {tool}")
    logger.info(f"🔍 ToolService实例: {id(tool_service)}")
    logger.info(f"🔍 config_dir: {tool_service.config_dir}")

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")

    if not tool.visible:
        raise HTTPException(status_code=403, detail="Tool is not available")

    try:
        # 处理会话：如果 session_id 不存在，创建新会话
        session_id = request.session_id
        session = None

        if not session_id:
            # 创建新会话
            session = session_service.create_session(
                user_id=current_user.user_id,
                tool_id=tool_id,
                title=request.message[:50]  # 使用消息前50字作为临时标题
            )
            session_id = session.session_id
            logger.info(f"✅ 创建新会话: {session_id}")
        else:
            # 获取现有会话
            session = await session_service.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
            if session.user_id != current_user.user_id:
                raise HTTPException(status_code=403, detail="Access denied")

        # 准备消息历史
        if request.history:
            # 使用请求中提供的历史
            history_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.history
            ]
        else:
            # 从数据库读取历史
            db_messages = session_service.get_session_messages(session_id)
            history_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in db_messages
            ]

        # 保存用户消息（包含附件）
        attachments_data = None
        if request.attached_files:
            attachments_data = [
                {"id": att.id, "name": att.name, "type": att.type, "size": 0}
                for att in request.attached_files
            ]

        session_service.add_message(
            session_id=session_id,
            role="user",
            content=request.message,
            user_id=current_user.user_id,
            attachments=attachments_data
        )

        # 准备模型配置
        model_config = tool.model if tool.model else None

        # 处理附件
        attachment_contents = []
        if request.attached_files:
            from src.services.temp_file_service import TempFileService
            temp_file_service = TempFileService()

            for att in request.attached_files:
                content = None
                if att.type == "temp":
                    content_bytes = temp_file_service.get_file_content(att.id)
                    if content_bytes:
                        content = content_bytes.decode('utf-8', errors='ignore')
                elif att.type == "knowledge":
                    from src.services.knowledge_service import KnowledgeService
                    from src.database import get_async_db
                    async for db in get_async_db():
                        knowledge_service = KnowledgeService(db)
                        docs = await knowledge_service.batch_get_documents([att.id])
                        if docs:
                            content = docs[0].get("content")
                        break
                elif att.type == "party":
                    from src.services.party_activity_service import PartyActivityService
                    from src.database import get_async_db
                    async for db in get_async_db():
                        party_service = PartyActivityService(db)
                        docs = await party_service.batch_get_documents([att.id])
                        if docs:
                            content = docs[0].get("content")
                        break

                if content:
                    attachment_contents.append({"name": att.name, "content": content})

        # 构建带附件的 system_prompt
        if attachment_contents:
            system_prompt = ai_service.build_system_prompt_with_attachments(
                tool.system_prompt,
                attachment_contents
            )
        else:
            system_prompt = tool.system_prompt

        # 获取流式响应
        async def generate():
            try:
                # 首先发送 session_id 事件（如果是新会话）
                session_event = json.dumps({
                    "type": "session_id",
                    "session_id": session_id
                }, ensure_ascii=False)
                yield f"data: {session_event}\n\n"

                full_response = ""
                async for chunk in ai_service.chat_stream(
                    system_prompt=system_prompt,
                    history=history_messages,
                    user_message=request.message,
                    model_config=model_config
                ):
                    full_response += chunk
                    # 发送SSE格式数据
                    yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

                # 发送结束标记
                yield "data: [DONE]\n\n"

                # 保存AI消息
                session_service.add_message(
                    session_id=session_id,
                    role="assistant",
                    content=full_response,
                    user_id=current_user.user_id
                )
                logger.info(f"✅ AI 消息已保存")

                # 检查是否是第一轮对话，如果是则生成标题
                messages = session_service.get_messages_by_session(session_id, user_id=current_user.user_id)
                logger.info(f"📊 会话消息数量检查 - 会话ID: {session_id}, 消息数: {len(messages)}")

                if len(messages) == 2:  # 第一轮对话：1条用户消息 + 1条AI回复
                    try:
                        logger.info(f"🎯 检测到第一轮对话，开始生成会话标题 - 用户消息: {request.message[:50]}")
                        # 生成标题
                        title = await title_generator.generate_title(request.message, full_response)
                        # 更新会话标题
                        session_service.update_session_title(session_id, title, user_id=current_user.user_id)
                        logger.info(f"✅ 会话标题已生成并更新：{title}")
                        # 发送标题生成完成事件（包含 session_id，前端用于刷新列表）
                        yield f"data: {json.dumps({'type': 'title_generated', 'session_id': session_id, 'title': title}, ensure_ascii=False)}\n\n"
                    except Exception as e:
                        logger.error(f"❌ 生成会话标题失败，使用降级方案: {e}", exc_info=True)
                        # 降级方案：使用简单截取
                        try:
                            fallback_title = title_generator._fallback_title(request.message)
                            session_service.update_session_title(session_id, fallback_title, user_id=current_user.user_id)
                            logger.info(f"⚠️ 使用降级方案生成标题：{fallback_title}")
                            # 发送降级标题事件
                            yield f"data: {json.dumps({'type': 'title_generated', 'session_id': session_id, 'title': fallback_title}, ensure_ascii=False)}\n\n"
                        except Exception as e2:
                            logger.error(f"❌ 降级方案也失败了: {e2}", exc_info=True)
                else:
                    logger.info(f"⏭️ 非第一轮对话，跳过标题生成（消息数: {len(messages)}）")

            except Exception as e:
                logger.error(f"Chat stream error: {e}")
                error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
                yield f"data: {error_data}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tools/{tool_id}/chat", response_model=ChatResponse, tags=["对话"])
async def chat_non_stream(
    tool_id: str,
    request: ChatRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)],
    ai_service: AIService = Depends(get_ai_service),
    session_service: SessionService = Depends(get_session_service),
    tool_service: ToolService = Depends(get_tool_service),
    artifact_parser = Depends(get_artifact_parser),
    title_generator = Depends(get_title_generator),
):
    """
    非流式对话接口

    返回完整的AI响应
    """
    # 获取工具配置
    tool = tool_service.get_tool_by_id(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")

    if not tool.visible:
        raise HTTPException(status_code=403, detail="Tool is not available")

    try:
        # 处理会话
        session_id = request.session_id
        session = None

        if not session_id:
            # 创建新会话
            session = session_service.create_session(
                user_id=current_user.user_id,
                tool_id=tool_id,
                title=request.message[:50]
            )
            session_id = session.session_id
        else:
            # 获取现有会话
            session = await session_service.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
            if session.user_id != current_user.user_id:
                raise HTTPException(status_code=403, detail="Access denied")

        # 准备消息历史
        if request.history:
            history_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.history
            ]
        else:
            # 从数据库读取历史
            db_messages = session_service.get_session_messages(session_id)
            history_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in db_messages
            ]

        # 保存用户消息（包含附件）
        attachments_data = None
        if request.attached_files:
            attachments_data = [
                {"id": att.id, "name": att.name, "type": att.type, "size": 0}
                for att in request.attached_files
            ]

        session_service.add_message(
            session_id=session_id,
            role="user",
            content=request.message,
            user_id=current_user.user_id,
            attachments=attachments_data
        )

        # 获取AI响应
        model_config = tool.model if tool.model else None

        # 处理附件
        attachment_contents = []
        if request.attached_files:
            from src.services.temp_file_service import TempFileService
            temp_file_service = TempFileService()

            for att in request.attached_files:
                content = None
                if att.type == "temp":
                    content_bytes = temp_file_service.get_file_content(att.id)
                    if content_bytes:
                        content = content_bytes.decode('utf-8', errors='ignore')
                elif att.type == "knowledge":
                    from src.services.knowledge_service import KnowledgeService
                    from src.database import get_async_db
                    async for db in get_async_db():
                        knowledge_service = KnowledgeService(db)
                        docs = await knowledge_service.batch_get_documents([att.id])
                        if docs:
                            content = docs[0].get("content")
                        break
                elif att.type == "party":
                    from src.services.party_activity_service import PartyActivityService
                    from src.database import get_async_db
                    async for db in get_async_db():
                        party_service = PartyActivityService(db)
                        docs = await party_service.batch_get_documents([att.id])
                        if docs:
                            content = docs[0].get("content")
                        break

                if content:
                    attachment_contents.append({"name": att.name, "content": content})

        # 构建带附件的 system_prompt
        if attachment_contents:
            system_prompt = ai_service.build_system_prompt_with_attachments(
                tool.system_prompt,
                attachment_contents
            )
        else:
            system_prompt = tool.system_prompt

        response = await ai_service.chat(
            system_prompt=system_prompt,
            history=history_messages,
            user_message=request.message,
            model_config=model_config
        )

        # 保存AI消息
        session_service.add_message(
            session_id=session_id,
            role="assistant",
            content=response,
            user_id=current_user.user_id
        )

        # 解析成果物
        artifacts = artifact_parser.parse_from_markdown(response)

        # 检查是否是第一轮对话，如果是则生成标题
        messages = session_service.get_messages_by_session(session_id, user_id=current_user.user_id)
        logger.info(f"会话消息数量检查 - 会话ID: {session_id}, 消息数: {len(messages)}")

        if len(messages) == 2:  # 第一轮对话：1条用户消息 + 1条AI回复
            try:
                logger.info(f"检测到第一轮对话，开始生成会话标题 - 用户消息: {request.message[:50]}")
                # 生成标题
                title = await title_generator.generate_title(request.message, response)
                # 更新会话标题
                session_service.update_session_title(session_id, title, user_id=current_user.user_id)
                logger.info(f"会话标题已生成并更新：{title}")
            except Exception as e:
                logger.error(f"生成会话标题失败，使用降级方案: {e}", exc_info=True)
                # 降级方案：使用简单截取
                try:
                    fallback_title = title_generator._fallback_title(request.message)
                    session_service.update_session_title(session_id, fallback_title, user_id=current_user.user_id)
                    logger.info(f"使用降级方案生成标题：{fallback_title}")
                except Exception as e2:
                    logger.error(f"降级方案也失败了: {e2}", exc_info=True)
        else:
            logger.info(f"非第一轮对话，跳过标题生成")

        return ChatResponse(
            reply=response,
            artifacts=artifacts,
            session_id=session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
