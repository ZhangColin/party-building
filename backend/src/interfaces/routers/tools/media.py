# -*- coding: utf-8 -*-
"""
多模态生成路由

提供图片、音频、视频等多模态内容生成接口

迁移说明：从 backend/src/routers/tools.py 迁移到新架构
迁移日期：2026-03-01
"""
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from src.models import (
    UserInfo,
    MediaGenerateRequest,
    MediaGenerateResponse,
    Message,
    MultiModalContent,
)

from src.interfaces.auth import get_current_user
from src.interfaces.dependencies import (
    get_ai_service,
    get_session_service,
    get_tool_service,
    get_title_generator,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# 用于存储任务状态的字典（简单实现，生产环境建议使用Redis）
task_storage: dict[str, dict] = {}


def make_absolute_url(relative_url: str, request: Request) -> str:
    """
    将相对URL转换为绝对URL

    Args:
        relative_url: 相对URL（如 /static/media/audio/xxx.mp3）
        request: FastAPI Request对象

    Returns:
        绝对URL（如 http://localhost:8000/static/media/audio/xxx.mp3）
    """
    # 如果已经是绝对URL，直接返回
    if relative_url.startswith(('http://', 'https://')):
        return relative_url

    # 构建绝对URL
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}{relative_url}"


@router.post("/tools/{tool_id}/generate-media", response_model=MediaGenerateResponse, tags=["多模态生成"])
async def generate_media(
    tool_id: str,
    media_request: MediaGenerateRequest,
    http_request: Request,
    current_user: Annotated[UserInfo, Depends(get_current_user)] = None,
):
    """
    多模态内容生成（图片、音频、视频）

    - **tool_id**: 工具ID（必须是多模态工具）
    - **message**: 用户提示词
    - **session_id**: 会话ID（可选，首次为空）
    - **size**: 生成尺寸（可选）
    - **count**: 生成数量（可选，1-4）
    - **style**: 生成风格（可选）

    Returns:
        包含task_id的响应，客户端需要轮询查询生成结果
    """
    try:
        logger.info(f"收到多模态生成请求 - 工具: {tool_id}, size={media_request.size}, count={media_request.count}, style={media_request.style}")

        tool_service = get_tool_service()
        session_service = get_session_service()
        ai_service = get_ai_service()
        title_generator = get_title_generator()

        # 1. 获取工具配置
        tool = tool_service.get_tool_by_id(tool_id)
        if not tool:
            raise HTTPException(status_code=404, detail="工具不存在")

        # 验证是多模态工具
        if tool.content_type != "multimodal":
            raise HTTPException(
                status_code=400,
                detail=f"工具 {tool_id} 不支持多模态生成，请使用文本对话接口"
            )

        # 2. 创建或获取会话
        session_id = media_request.session_id
        if not session_id:
            # 首次生成，创建新会话
            session_id = str(uuid.uuid4())

            # 生成会话标题（只传用户提示词，不传AI回复）
            title = await title_generator.generate_title(
                user_message=media_request.message,
                ai_response=None
            )

            # 保存会话到数据库
            await session_service.create_session_with_id(
                session_id=session_id,
                user_id=current_user.user_id,
                tool_id=tool_id,
                title=title
            )

            logger.info(f"创建新会话 - session_id: {session_id}, 标题: {title}")
        else:
            # 验证会话所有权
            session = await session_service.get_session(session_id)
            if not session or session.user_id != current_user.user_id:
                raise HTTPException(status_code=403, detail="无权访问此会话")

        # 3. 保存用户消息
        user_message_id = str(uuid.uuid4())
        await session_service.save_message(
            message_id=user_message_id,
            session_id=session_id,
            role="user",
            content=media_request.message
        )

        # 4. 调用AI服务生成内容
        task_id = str(uuid.uuid4())

        try:
            # 根据媒体类型调用不同的生成方法
            if tool.media_type == "image":
                return await _handle_image_generation(
                    tool, media_request, session_id, user_message_id,
                    task_id, session_service, ai_service
                )
            elif tool.media_type == "audio":
                return await _handle_audio_generation(
                    tool, media_request, session_id, user_message_id,
                    task_id, session_service, ai_service, http_request
                )
            elif tool.media_type == "video":
                return await _handle_video_generation(
                    tool, media_request, session_id, user_message_id,
                    task_id, session_service, ai_service
                )
            else:
                raise HTTPException(status_code=400, detail=f"不支持的媒体类型: {tool.media_type}")

        except Exception as e:
            logger.error(f"调用AI生成服务失败: {e}", exc_info=True)
            raise HTTPException(status_code=503, detail=f"AI服务调用失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"多模态生成接口异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def _handle_image_generation(
    tool, media_request, session_id, user_message_id, task_id,
    session_service, ai_service
):
    """处理图片生成"""
    logger.info(f"开始调用GLM图像生成 - 提示词: {media_request.message[:50]}...")

    glm_result = await ai_service.generate_image(
        prompt=media_request.message,
        model_config=tool.model or "glm:cogview-4",
        size=media_request.size,
        count=media_request.count,
        style=media_request.style
    )

    logger.info(f"GLM返回结果: {glm_result}")

    # 检查GLM是同步还是异步返回
    if glm_result.get("mode") == "sync":
        # 同步模式：GLM直接返回了图片
        image_data = glm_result.get("data", [])
        media_urls = [img.get("url") for img in image_data if img.get("url")]

        logger.info(f"获取到 {len(media_urls)} 张图片")

        # 构建元数据
        metadata = {
            "size": media_request.size,
            "count": len(media_urls),
            "style": media_request.style
        }

        # 直接保存AI回复消息
        ai_message_id = str(uuid.uuid4())
        media_content_obj = MultiModalContent(
            content_type="image",
            media_urls=media_urls,
            metadata=metadata
        )

        ai_message = Message(
            message_id=ai_message_id,
            session_id=session_id,
            role="assistant",
            content="",
            created_at=None
        )
        ai_message.set_media_content(media_content_obj)

        await session_service.save_message_with_media(
            message_id=ai_message_id,
            session_id=session_id,
            role="assistant",
            content="",
            media_content=ai_message.media_content
        )

        # 标记为同步模式，直接返回完成状态
        task_storage[task_id] = {
            "session_id": session_id,
            "status": "completed",
            "media_urls": media_urls,
            "metadata": metadata
        }

        logger.info(f"同步生成完成 - task_id: {task_id}, 图片数量: {len(media_urls)}")

        # 直接返回完成状态，不需要前端轮询
        return MediaGenerateResponse(
            session_id=session_id,
            message_id=ai_message_id,
            task_id=task_id,
            status="completed",
            media_urls=media_urls,
            content_type="image"
        )
    else:
        # 异步模式：需要轮询
        async_result = glm_result.get("result", {})
        glm_task_id = async_result.get("id") or async_result.get("task_id")

        # 存储任务状态
        task_storage[task_id] = {
            "glm_task_id": glm_task_id,
            "session_id": session_id,
            "message_id": user_message_id,
            "tool_id": tool_id,
            "media_type": tool.media_type,
            "status": "processing",
            "request_params": {
                "size": media_request.size,
                "count": media_request.count,
                "style": media_request.style
            },
            "query_fail_count": 0
        }

        logger.info(f"异步任务已提交 - task_id: {task_id}, glm_task_id: {glm_task_id}")

        return MediaGenerateResponse(
            session_id=session_id,
            message_id=user_message_id,
            task_id=task_id,
            status="processing"
        )


async def _handle_audio_generation(
    tool, media_request, session_id, user_message_id,
    task_id, session_service, ai_service, http_request
):
    """处理音频生成"""
    logger.info(f"开始调用GLM音频生成 - 文本: {media_request.message[:50]}...")

    glm_result = await ai_service.generate_audio(
        prompt=media_request.message,
        model_config=tool.model or "glm:glm-tts",
        voice=media_request.voice if hasattr(media_request, 'voice') else None
    )

    logger.info(f"GLM返回结果: {glm_result}")

    # GLM-TTS是同步返回
    if glm_result.get("mode") == "sync":
        # 提取音频URLs
        audio_data = glm_result.get("data", [])
        media_urls = [audio.get("url") for audio in audio_data if audio.get("url")]

        # 将相对URL转换为绝对URL（确保前端可以正确访问）
        media_urls = [make_absolute_url(url, http_request) for url in media_urls]

        logger.info(f"获取到 {len(media_urls)} 个音频")

        # 构建元数据
        metadata = {
            "text_length": len(media_request.message),
            "voice": media_request.voice if hasattr(media_request, 'voice') else "default"
        }

        # 保存AI回复消息（包含音频URLs）
        ai_message_id = str(uuid.uuid4())
        media_content_obj = MultiModalContent(
            content_type="audio",
            media_urls=media_urls,
            metadata=metadata
        )

        ai_message = Message(
            message_id=ai_message_id,
            session_id=session_id,
            role="assistant",
            content="",
            created_at=None
        )
        ai_message.set_media_content(media_content_obj)

        await session_service.save_message_with_media(
            message_id=ai_message_id,
            session_id=session_id,
            role="assistant",
            content="",
            media_content=ai_message.media_content
        )

        # 标记为同步模式，直接返回完成状态
        task_storage[task_id] = {
            "session_id": session_id,
            "status": "completed",
            "media_urls": media_urls,
            "metadata": metadata
        }

        logger.info(f"同步生成完成 - task_id: {task_id}, 音频数量: {len(media_urls)}")

        # 直接返回完成状态，不需要前端轮询
        return MediaGenerateResponse(
            session_id=session_id,
            message_id=ai_message_id,
            task_id=task_id,
            status="completed",
            media_urls=media_urls,
            content_type="audio"
        )


async def _handle_video_generation(
    tool, media_request, session_id, user_message_id,
    task_id, session_service, ai_service
):
    """处理视频生成"""
    logger.info(f"开始调用GLM视频生成 - 提示词: {media_request.message[:50]}...")

    glm_result = await ai_service.generate_video(
        prompt=media_request.message,
        model_config=tool.model or "glm:cogvideox-2",
        size=media_request.size,
        fps=media_request.fps if hasattr(media_request, 'fps') else None,
        quality=media_request.quality if hasattr(media_request, 'quality') else None,
        with_audio=media_request.with_audio if hasattr(media_request, 'with_audio') else False
    )

    logger.info(f"GLM返回结果: {glm_result}")

    # CogVideoX是异步返回，需要轮询
    if glm_result.get("mode") == "async":
        async_result = glm_result.get("result", {})
        glm_task_id = async_result.get("id") or async_result.get("task_id")

        # 存储任务状态
        task_storage[task_id] = {
            "glm_task_id": glm_task_id,
            "session_id": session_id,
            "message_id": user_message_id,
            "tool_id": tool.tool_id,
            "media_type": tool.media_type,
            "status": "processing",
            "request_params": {
                "size": media_request.size,
                "fps": media_request.fps if hasattr(media_request, 'fps') else None,
                "quality": media_request.quality if hasattr(media_request, 'quality') else None
            },
            "query_fail_count": 0
        }

        logger.info(f"异步任务已提交 - task_id: {task_id}, glm_task_id: {glm_task_id}")

    return MediaGenerateResponse(
        session_id=session_id,
        message_id=user_message_id,
        task_id=task_id,
        status="processing"
    )
