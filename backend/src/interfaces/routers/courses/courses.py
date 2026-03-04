# -*- coding: utf-8 -*-
"""课程文档路由

包含课程目录、课程文档管理等接口。
"""
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, status, Depends, File, Form, UploadFile

from src.models import (
    UserInfo,
    CourseCategoryTreeResponse,
    CourseDocumentListResponse,
    CourseDocumentDetail,
    AdminCourseCategoryListResponse,
    AdminCourseCategoryListItem,
    CreateCourseCategoryRequest,
    UpdateCourseCategoryRequest,
    AdminCourseDocumentListResponse,
    AdminCourseDocumentListItem,
    UpdateCourseDocumentRequest,
)

from src.interfaces.dependencies import get_course_service, get_current_user, require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["课程文档"])


# ==================== 课程文档模块 API ====================

@router.get("/documents/categories", response_model=CourseCategoryTreeResponse)
async def get_course_category_tree(current_user: Annotated[UserInfo, Depends(get_current_user)] = None):
    """
    获取课程目录树结构

    Returns:
        CourseCategoryTreeResponse: 目录树，包含所有层级的目录
    """
    try:
        course_service = get_course_service()
        result = course_service.get_category_tree()
        return result
    except Exception as e:
        logger.error(f"获取课程目录树失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取课程目录树失败"
        )


@router.get("/documents/category/{category_id}/documents", response_model=CourseDocumentListResponse)
async def get_course_documents_by_category(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)] = None,
):
    """
    获取指定目录下的文档列表

    Args:
        category_id: 目录ID

    Returns:
        CourseDocumentListResponse: 文档列表
    """
    try:
        course_service = get_course_service()
        result = course_service.get_documents_by_category(category_id)
        return result
    except Exception as e:
        logger.error(f"获取目录文档列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取目录文档列表失败"
        )


@router.get("/documents/{doc_id}", response_model=CourseDocumentDetail)
async def get_course_document_detail(
    doc_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)] = None,
):
    """
    获取文档详情

    Args:
        doc_id: 文档ID

    Returns:
        CourseDocumentDetail: 文档详情，包含Markdown内容和上下文导航

    Raises:
        HTTPException: 文档不存在时返回404
    """
    try:
        course_service = get_course_service()
        result = course_service.get_document_detail(doc_id)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档详情失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取文档详情失败"
        )


# ==================== 后台管理 - 课程目录管理接口 ====================

@router.get("/admin/course-categories", response_model=AdminCourseCategoryListResponse)
async def get_admin_course_categories(
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """获取课程目录列表（管理后台）"""
    try:
        course_service = get_course_service()
        return course_service.get_admin_categories()
    except Exception as e:
        logger.error(f"获取课程目录列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/course-categories", status_code=status.HTTP_201_CREATED)
async def create_course_category(
    request: CreateCourseCategoryRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """创建课程目录（管理后台）"""
    try:
        course_service = get_course_service()
        category = course_service.create_category(request)
        return {"message": "目录创建成功", "category": category}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建课程目录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/admin/course-categories/{category_id}")
async def update_course_category(
    category_id: str,
    request: UpdateCourseCategoryRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """更新课程目录（管理后台）"""
    try:
        course_service = get_course_service()
        category = course_service.update_category(category_id, request)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="目录不存在"
            )
        return {"message": "目录更新成功", "category": category}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新课程目录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/admin/course-categories/{category_id}")
async def delete_course_category(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """删除课程目录（管理后台）"""
    try:
        course_service = get_course_service()
        success, error_msg = course_service.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        return {"message": "目录删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除课程目录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/course-categories/{category_id}/move-up")
async def move_course_category_up(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """上移课程目录（管理后台）"""
    try:
        course_service = get_course_service()
        success, error_msg = course_service.move_category_up(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        return {"message": "目录已上移"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上移课程目录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/course-categories/{category_id}/move-down")
async def move_course_category_down(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """下移课程目录（管理后台）"""
    try:
        course_service = get_course_service()
        success, error_msg = course_service.move_category_down(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        return {"message": "目录已下移"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下移课程目录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== 后台管理 - 课程文档管理接口 ====================

@router.get("/admin/course-documents", response_model=AdminCourseDocumentListResponse)
async def get_admin_course_documents(
    page: int = 1,
    page_size: int = 20,
    category_id: Optional[str] = None,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """获取课程文档列表（管理后台）"""
    try:
        course_service = get_course_service()
        return course_service.get_admin_documents(
            page=page,
            page_size=page_size,
            category_id=category_id
        )
    except Exception as e:
        logger.error(f"获取课程文档列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/course-documents", status_code=status.HTTP_201_CREATED)
async def create_course_document(
    title: str = Form(...),
    summary: str = Form(...),
    category_id: str = Form(...),
    order: int = Form(0),
    markdown_file: UploadFile = File(...),
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """创建课程文档（管理后台）"""
    try:
        # 验证文件类型
        if not markdown_file.filename.endswith(('.md', '.markdown')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持.md或.markdown文件"
            )

        # 验证文件大小（5MB）
        content = await markdown_file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过5MB限制"
            )

        # 解码Markdown内容
        markdown_content = content.decode('utf-8')

        # 创建文档
        course_service = get_course_service()
        document = course_service.create_document(
            title=title,
            summary=summary,
            category_id=category_id,
            markdown_content=markdown_content,
            order=order
        )

        return {"message": "文档创建成功", "document": document}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建课程文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/admin/course-documents/{doc_id}")
async def update_course_document(
    doc_id: str,
    request: UpdateCourseDocumentRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """更新课程文档（管理后台）"""
    try:
        course_service = get_course_service()
        document = course_service.update_document(doc_id, request)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )
        return {"message": "文档更新成功", "document": document}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新课程文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/admin/course-documents/{doc_id}")
async def delete_course_document(
    doc_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """删除课程文档（管理后台）"""
    try:
        course_service = get_course_service()
        success, error_msg = course_service.delete_document(doc_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        return {"message": "文档删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除课程文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/course-documents/{doc_id}/move-up")
async def move_course_document_up(
    doc_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """上移课程文档（管理后台）"""
    try:
        course_service = get_course_service()
        success, error_msg = course_service.move_document_up(doc_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        return {"message": "文档已上移"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上移课程文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/course-documents/{doc_id}/move-down")
async def move_course_document_down(
    doc_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """下移课程文档（管理后台）"""
    try:
        course_service = get_course_service()
        success, error_msg = course_service.move_document_down(doc_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        return {"message": "文档已下移"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下移课程文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
