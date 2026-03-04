# -*- coding: utf-8 -*-
"""教案学案路由

包含作品管理、作品分类管理等接口。
"""
import logging
import shutil
import uuid
from pathlib import Path
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, status, Depends, File, Form, UploadFile

from src.models import (
    UserInfo,
    WorkCategoryResponse,
    WorkDetail,
    AdminWorkListResponse,
    AdminWorkListItem,
    CreateWorkResponse,
    UpdateWorkRequest,
    UpdateWorkResponse,
    MoveWorkResponse,
    ToggleWorkVisibilityResponse,
    AdminWorkCategoryListResponse,
    AdminWorkCategoryListItem,
    CreateWorkCategoryRequest,
    CreateWorkCategoryResponse,
    UpdateWorkCategoryRequest,
    UpdateWorkCategoryResponse,
    MoveWorkCategoryResponse,
)

from src.interfaces.auth import get_current_user
from src.interfaces.dependencies import get_work_service, require_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["作品管理"])


# ==================== 作品展示模块 API ====================

@router.get("/works/categories", response_model=WorkCategoryResponse)
async def get_work_categories(current_user: Annotated[UserInfo, Depends(get_current_user)] = None):
    """
    获取所有作品分类及其下的作品列表

    Returns:
        WorkCategoryResponse: 分类列表，每个分类包含该分类下的作品列表

    Notes:
        - 只返回 visible=True 的作品
        - 分类按 order 字段升序排列
        - 每个分类下的作品按 order 字段升序排列
        - 如果某个分类下没有可见作品，则不返回该分类
    """
    try:
        work_service = get_work_service()
        result = work_service.get_categories_with_works()
        return result
    except Exception as e:
        logger.error(f"获取作品分类列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取作品分类列表失败"
        )


@router.get("/works/{work_id}", response_model=WorkDetail)
async def get_work_detail(
    work_id: str,
    current_user: Annotated[UserInfo, Depends(get_current_user)] = None,
):
    """
    获取指定作品的详细信息

    Args:
        work_id: 作品ID

    Returns:
        WorkDetail: 作品详情（包括分类信息、HTML访问URL等）

    Raises:
        HTTPException: 作品不存在或不可见时返回404

    Notes:
        - 只能查询 visible=True 的作品
        - html_path 会被转换为完整的访问URL
    """
    try:
        work_service = get_work_service()
        result = work_service.get_work_detail(work_id)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="作品不存在或已下线"
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取作品详情失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取作品详情失败"
        )


# ==================== 后台管理 - 作品管理接口 ====================

@router.get("/admin/works", response_model=AdminWorkListResponse)
async def get_admin_works(
    page: int = 1,
    page_size: int = 20,
    category_id: Optional[str] = None,
    visible: Optional[bool] = None,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """获取作品列表（管理后台）"""
    try:
        work_service = get_work_service()
        return work_service.get_all_works_admin(
            page=page,
            page_size=page_size,
            category_id=category_id,
            visible=visible
        )
    except Exception as e:
        logger.error(f"获取作品列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/works", response_model=CreateWorkResponse, status_code=status.HTTP_201_CREATED)
async def create_work(
    name: str = Form(...),
    description: str = Form(...),
    category_id: str = Form(...),
    icon: Optional[str] = Form(None),
    order: int = Form(0),
    visible: bool = Form(True),
    html_file: UploadFile = File(...),
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """上传作品（管理后台）"""
    try:
        # 验证文件类型
        if not html_file.filename.endswith('.html'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持.html文件"
            )

        # 验证文件大小（10MB）
        content = await html_file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过10MB限制"
            )

        # 生成作品ID
        work_id = str(uuid.uuid4())[:8]

        # 创建存储目录
        work_dir = Path(__file__).parent.parent.parent / "static" / "works" / "html" / work_id
        work_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = work_dir / "index.html"
        with open(file_path, "wb") as f:
            f.write(content)

        # 数据库存储相对路径
        html_path = f"works/html/{work_id}/index.html"

        # 创建作品记录
        work_service = get_work_service()
        work = work_service.create_work(
            name=name,
            description=description,
            category_id=category_id,
            html_path=html_path,
            icon=icon,
            order=order,
            visible=visible
        )

        return CreateWorkResponse(work=work)

    except ValueError as e:
        if "分类不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/admin/works/{work_id}", response_model=UpdateWorkResponse)
async def update_work(
    work_id: str,
    request: UpdateWorkRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """更新作品信息（管理后台）"""
    try:
        work_service = get_work_service()
        work = work_service.update_work(work_id, request)
        return UpdateWorkResponse(work=work)
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/admin/works/{work_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work(
    work_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """删除作品（管理后台）"""
    try:
        work_service = get_work_service()
        html_path = work_service.delete_work(work_id)

        # 删除文件
        if html_path:
            file_path = Path(__file__).parent.parent.parent / "static" / html_path
            if file_path.exists():
                work_dir = file_path.parent
                shutil.rmtree(work_dir, ignore_errors=True)

        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/admin/works/{work_id}/move-up", response_model=MoveWorkResponse)
async def move_work_up(
    work_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """上移作品（管理后台）"""
    try:
        work_service = get_work_service()
        work = work_service.move_work_up(work_id)
        return MoveWorkResponse(message="作品已上移", work=work)
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/admin/works/{work_id}/move-down", response_model=MoveWorkResponse)
async def move_work_down(
    work_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """下移作品（管理后台）"""
    try:
        work_service = get_work_service()
        work = work_service.move_work_down(work_id)
        return MoveWorkResponse(message="作品已下移", work=work)
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/admin/works/{work_id}/toggle-visibility", response_model=ToggleWorkVisibilityResponse)
async def toggle_work_visibility(
    work_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """切换作品可见性（管理后台）"""
    try:
        work_service = get_work_service()
        work, message = work_service.toggle_work_visibility(work_id)
        return ToggleWorkVisibilityResponse(message=message, work=work)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== 后台管理 - 作品分类管理接口 ====================

@router.get("/admin/work-categories", response_model=AdminWorkCategoryListResponse)
async def get_admin_work_categories(
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """获取作品分类列表（管理后台）"""
    try:
        work_service = get_work_service()
        return work_service.get_all_categories_admin()
    except Exception as e:
        logger.error(f"获取作品分类列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/admin/work-categories", response_model=CreateWorkCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_work_category(
    request: CreateWorkCategoryRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """创建作品分类（管理后台）"""
    try:
        work_service = get_work_service()
        category = work_service.create_category(request)
        return CreateWorkCategoryResponse(category=category)
    except ValueError as e:
        if "已存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/admin/work-categories/{category_id}", response_model=UpdateWorkCategoryResponse)
async def update_work_category(
    category_id: str,
    request: UpdateWorkCategoryRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """更新作品分类（管理后台）"""
    try:
        work_service = get_work_service()
        category = work_service.update_category(category_id, request)
        return UpdateWorkCategoryResponse(category=category)
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "已被使用" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/admin/work-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_category(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """删除作品分类（管理后台）"""
    try:
        work_service = get_work_service()
        work_service.delete_category(category_id)
        return None
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "还有" in str(e) and "作品" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/admin/work-categories/{category_id}/move-up", response_model=MoveWorkCategoryResponse)
async def move_work_category_up(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """上移作品分类（管理后台）"""
    try:
        work_service = get_work_service()
        category = work_service.move_category_up(category_id)
        return MoveWorkCategoryResponse(message="分类已上移", category=category)
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/admin/work-categories/{category_id}/move-down", response_model=MoveWorkCategoryResponse)
async def move_work_category_down(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """下移作品分类（管理后台）"""
    try:
        work_service = get_work_service()
        category = work_service.move_category_down(category_id)
        return MoveWorkCategoryResponse(message="分类已下移", category=category)
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
