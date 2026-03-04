# -*- coding: utf-8 -*-
"""通用功能路由

包含导航、文档转换、任务状态查询等通用接口。

迁移说明：从 backend/src/routers/common.py 迁移到新架构
迁移日期：2026-03-02
"""
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends

from src.models import (
    UserInfo,
    NavigationModule,
    NavigationResponse,
    MarkdownToWordRequest,
    TaskStatusResponse,
    MultiModalContent,
    Message,
    CommonToolCategoryResponse,
)

from src.interfaces.auth import get_current_user
from src.interfaces.dependencies import (
    get_config_loader,
    get_conversion_service,
    get_session_service,
    get_ai_service,
    get_common_tool_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["通用功能"])


# 用于存储任务状态的字典（简单实现，生产环境建议使用Redis）
# 从 tools.py 迁移过来（2026-03-01）
task_storage: dict[str, dict] = {}


@router.get("/navigation", response_model=NavigationResponse)
async def get_navigation():
    """获取顶部导航模块配置（公开接口，无需认证）"""
    config_loader = get_config_loader()
    modules = config_loader.load_navigation()
    return NavigationResponse(modules=modules)


@router.get("/common-tools/categories", response_model=CommonToolCategoryResponse)
async def get_common_tool_categories():
    """
    获取常用工具分类列表（包含每个分类下的工具列表）

    这是一个公开接口，无需认证。返回所有可见的工具分类及其下的工具列表，
    按分类的 order 字段排序。

    Returns:
        CommonToolCategoryResponse: 分类列表响应，包含每个分类及其工具
    """
    try:
        common_tool_service = get_common_tool_service()
        return common_tool_service.get_categories_with_tools()
    except Exception as e:
        logger.error(f"获取常用工具分类失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取工具分类失败，请稍后重试"
        )


@router.post("/convert/markdown-to-word")
async def convert_markdown_to_word(
    request: MarkdownToWordRequest,
    current_user: Annotated[UserInfo, Depends(get_current_user)] = None,
):
    """
    将 Markdown 内容转换为 Word 文档并下载

    - **content**: Markdown 内容（必填）
    - **filename**: 文件名（可选，不含扩展名）

    Returns:
        Word 文档文件（application/vnd.openxmlformats-officedocument.wordprocessingml.document）
    """
    try:
        # 调用转换服务
        conversion_service = get_conversion_service()
        word_content, filename = conversion_service.markdown_to_word(
            markdown_content=request.content,
            filename=request.filename
        )

        # 返回 Word 文件
        from fastapi.responses import Response
        return Response(
            content=word_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        # pandoc 不可用或转换失败
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"文档转换服务暂时不可用: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Markdown 转 Word 失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文档转换失败，请稍后重试"
        )


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)] = None,
):
    """
    查询任务生成状态

    - **task_id**: 任务ID

    Returns:
        任务状态，包括进度、结果URL等
    """
    try:
        # 1. 获取任务信息
        task_info = task_storage.get(task_id)
        if not task_info:
            raise HTTPException(status_code=404, detail="任务不存在")

        # 2. 验证会话所有权
        session_id = task_info["session_id"]
        session_service = get_session_service()
        session = await session_service.get_session(session_id)
        if not session or session.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="无权访问此任务")

        # 3. 检查任务状态
        # 如果任务已经完成（同步模式），直接返回结果
        if task_info.get("status") == "completed":
            logger.info(f"任务已完成（同步模式） - task_id: {task_id}")
            return TaskStatusResponse(
                task_id=task_id,
                status="completed",
                media_urls=task_info.get("media_urls", []),
                metadata=task_info.get("metadata", {})
            )

        # 4. 异步模式：查询GLM任务状态
        glm_task_id = task_info.get("glm_task_id")
        if not glm_task_id:
            # 没有 glm_task_id 说明是同步模式，但状态不是 completed
            # 这种情况不应该发生，返回错误
            logger.error(f"任务没有 glm_task_id，且状态不是 completed - task_id: {task_id}, task_info: {task_info}")
            raise HTTPException(status_code=500, detail="任务状态异常")

        media_type = task_info["media_type"]
        ai_service = get_ai_service()

        try:
            if media_type == "image":
                logger.info(f"查询GLM任务状态 - task_id: {task_id}, glm_task_id: {glm_task_id}")
                glm_result = await ai_service.get_image_result(glm_task_id)

                # 解析GLM返回结果
                task_status = glm_result.get("task_status", "PROCESSING")
                logger.info(f"GLM任务状态: {task_status}")

                if task_status == "SUCCESS":
                    # 提取图片URLs
                    image_result = glm_result.get("image_result", [])
                    media_urls = [img.get("url") for img in image_result if img.get("url")]

                    # 构建元数据
                    metadata = {
                        "size": task_info["request_params"]["size"],
                        "count": len(media_urls),
                        "style": task_info["request_params"]["style"]
                    }

                    # 保存AI回复消息（包含图片URLs）
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
                        content="",  # 多模态消息无文本内容
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

                    # 更新任务状态为已完成
                    task_storage[task_id]["status"] = "completed"

                    logger.info(f"任务完成 - task_id: {task_id}, 图片数量: {len(media_urls)}")

                    return TaskStatusResponse(
                        task_id=task_id,
                        status="completed",
                        content_type="image",
                        media_urls=media_urls,
                        metadata=metadata
                    )

                elif task_status == "FAIL" or task_status == "FAILED":
                    # 生成失败
                    error_info = glm_result.get("error", {})
                    error_message = error_info.get("message", "生成失败")

                    # 更新任务状态
                    task_storage[task_id]["status"] = "failed"
                    task_storage[task_id]["error"] = error_message

                    logger.warning(f"任务失败 - task_id: {task_id}, 错误: {error_message}")

                    return TaskStatusResponse(
                        task_id=task_id,
                        status="failed",
                        error_message=error_message
                    )

                else:
                    # 仍在处理中
                    # GLM可能不返回progress，我们可以估算一个
                    return TaskStatusResponse(
                        task_id=task_id,
                        status="processing",
                        progress=50  # 简单返回50%
                    )

            elif media_type == "video":
                logger.info(f"查询GLM视频任务状态 - task_id: {task_id}, glm_task_id: {glm_task_id}")
                glm_result = await ai_service.get_video_result(glm_task_id)

                # 解析GLM返回结果（视频使用与图片相同的接口）
                task_status = glm_result.get("task_status", "PROCESSING")
                logger.info(f"GLM视频任务状态: {task_status}")

                if task_status == "SUCCESS":
                    # 提取视频URLs
                    video_result = glm_result.get("video_result", [])
                    media_urls = [video.get("url") for video in video_result if video.get("url")]

                    # 构建元数据
                    metadata = {
                        "size": task_info["request_params"].get("size"),
                        "fps": task_info["request_params"].get("fps"),
                        "quality": task_info["request_params"].get("quality"),
                        "duration": 6  # CogVideoX默认生成6秒视频
                    }

                    # 保存AI回复消息（包含视频URLs）
                    ai_message_id = str(uuid.uuid4())
                    media_content_obj = MultiModalContent(
                        content_type="video",
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

                    # 更新任务状态为已完成
                    task_storage[task_id]["status"] = "completed"

                    logger.info(f"视频任务完成 - task_id: {task_id}, 视频数量: {len(media_urls)}")

                    return TaskStatusResponse(
                        task_id=task_id,
                        status="completed",
                        content_type="video",
                        media_urls=media_urls,
                        metadata=metadata
                    )

                elif task_status == "FAIL" or task_status == "FAILED":
                    # 生成失败
                    error_info = glm_result.get("error", {})
                    error_message = error_info.get("message", "视频生成失败")

                    # 更新任务状态
                    task_storage[task_id]["status"] = "failed"
                    task_storage[task_id]["error"] = error_message

                    logger.warning(f"视频任务失败 - task_id: {task_id}, 错误: {error_message}")

                    return TaskStatusResponse(
                        task_id=task_id,
                        status="failed",
                        error_message=error_message
                    )

                else:
                    # 仍在处理中（视频生成通常需要30秒左右）
                    return TaskStatusResponse(
                        task_id=task_id,
                        status="processing",
                        progress=50
                    )

            else:
                # 其他媒体类型
                raise HTTPException(status_code=501, detail=f"媒体类型 {media_type} 暂不支持")

        except Exception as e:
            logger.error(f"查询GLM任务状态失败: {e}", exc_info=True)

            # 增加失败计数
            task_storage[task_id]["query_fail_count"] = task_storage[task_id].get("query_fail_count", 0) + 1
            fail_count = task_storage[task_id]["query_fail_count"]

            # 如果失败次数超过5次，标记任务为失败
            if fail_count >= 5:
                task_storage[task_id]["status"] = "failed"
                logger.error(f"任务查询失败次数过多，标记为失败 - task_id: {task_id}")
                return TaskStatusResponse(
                    task_id=task_id,
                    status="failed",
                    error_message=f"查询任务状态失败: {str(e)}"
                )

            # 否则返回处理中状态，让前端继续轮询
            logger.warning(f"查询任务状态失败 ({fail_count}/5次)，将在下次查询时重试")
            return TaskStatusResponse(
                task_id=task_id,
                status="processing",
                progress=None
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询任务状态接口异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
