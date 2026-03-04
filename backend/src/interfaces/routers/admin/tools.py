# -*- coding: utf-8 -*-
"""管理员工具路由

提供内置工具和工具分类的管理接口
"""
import logging
import shutil
import uuid
from pathlib import Path
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, status, Depends, File, Form, UploadFile

from src.models import (
    UserInfo,
    AdminCommonToolListResponse,
    AdminCommonToolListItem,
    CreateBuiltInToolRequest,
    CreateToolResponse,
    UpdateToolRequest,
    UpdateToolResponse,
    MoveToolResponse,
    ToggleVisibilityResponse,
    AdminToolCategoryListResponse,
    AdminToolCategoryListItem,
    CreateToolCategoryRequest,
    CreateToolCategoryResponse,
    UpdateToolCategoryRequest,
    UpdateToolCategoryResponse,
    MoveCategoryResponse,
)

from src.interfaces.auth import get_current_user
from src.interfaces.dependencies import get_common_tool_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["管理员工具"])


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


# ==================== 常用工具管理接口 ====================

@router.get("/common-tools", response_model=AdminCommonToolListResponse)
async def get_admin_tools(
    page: int = 1,
    page_size: int = 20,
    category_id: Optional[str] = None,
    type: Optional[str] = None,
    visible: Optional[bool] = None,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """获取工具列表（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        return common_tool_service.get_all_tools_admin(
            page=page,
            page_size=page_size,
            category_id=category_id,
            tool_type=type,
            visible=visible
        )
    except Exception as e:
        logger.error(f"获取工具列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/common-tools/built-in", response_model=CreateToolResponse, status_code=status.HTTP_201_CREATED)
async def create_built_in_tool(
    request: CreateBuiltInToolRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """创建内置工具（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        tool = common_tool_service.create_built_in_tool(request)
        return CreateToolResponse(tool=tool)
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


@router.post("/common-tools/html", response_model=CreateToolResponse, status_code=status.HTTP_201_CREATED)
async def create_html_tool(
    name: str = Form(...),
    description: str = Form(...),
    category_id: str = Form(...),
    icon: Optional[str] = Form(None),
    order: int = Form(0),
    visible: bool = Form(True),
    html_file: UploadFile = File(...),
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """上传HTML工具（管理后台）"""
    try:
        # 验证文件类型
        if not html_file.filename.endswith('.html'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持.html文件"
            )

        # 验证文件大小（5MB）
        content = await html_file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文件大小超过5MB限制"
            )

        # 生成工具ID（使用UUID前8位确保唯一性且简短）
        tool_id = str(uuid.uuid4())[:8]

        # 创建存储目录
        # Path(__file__) = backend/src/interfaces/routers/admin/tools.py
        # parent.parent.parent.parent.parent = backend
        tool_dir = Path(__file__).parent.parent.parent.parent.parent / "static" / "common_tools" / "html" / tool_id
        tool_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = tool_dir / "index.html"
        with open(file_path, "wb") as f:
            f.write(content)

        # 数据库存储相对路径
        html_path = f"common_tools/html/{tool_id}/index.html"

        # 创建工具记录
        common_tool_service = get_common_tool_service()
        tool = common_tool_service.create_html_tool(
            name=name,
            description=description,
            category_id=category_id,
            html_path=html_path,
            icon=icon,
            order=order,
            visible=visible
        )

        return CreateToolResponse(tool=tool)

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


@router.patch("/common-tools/{tool_id}", response_model=UpdateToolResponse)
async def update_tool(
    tool_id: str,
    request: UpdateToolRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """更新工具信息（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        tool = common_tool_service.update_tool(tool_id, request)
        return UpdateToolResponse(tool=tool)
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


@router.delete("/common-tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """删除工具（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        html_path = common_tool_service.delete_tool(tool_id)

        # 如果是HTML工具，删除文件
        if html_path:
            # Path(__file__) = backend/src/interfaces/routers/admin/tools.py
            # parent.parent.parent.parent.parent = backend
            file_path = Path(__file__).parent.parent.parent.parent.parent / "static" / html_path
            if file_path.exists():
                # 删除整个工具目录
                tool_dir = file_path.parent
                shutil.rmtree(tool_dir, ignore_errors=True)

        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/common-tools/{tool_id}/move-up", response_model=MoveToolResponse)
async def move_tool_up(
    tool_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """上移工具（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        tool = common_tool_service.move_tool_up(tool_id)
        return MoveToolResponse(message="工具已上移", tool=tool)
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


@router.post("/common-tools/{tool_id}/move-down", response_model=MoveToolResponse)
async def move_tool_down(
    tool_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """下移工具（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        tool = common_tool_service.move_tool_down(tool_id)
        return MoveToolResponse(message="工具已下移", tool=tool)
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


@router.post("/common-tools/{tool_id}/toggle-visibility", response_model=ToggleVisibilityResponse)
async def toggle_tool_visibility(
    tool_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """切换工具可见性（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        tool, message = common_tool_service.toggle_tool_visibility(tool_id)
        return ToggleVisibilityResponse(message=message, tool=tool)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ==================== 工具分类管理接口 ====================

@router.get("/tool-categories", response_model=AdminToolCategoryListResponse)
async def get_admin_tool_categories(
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """获取工具分类列表（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        return common_tool_service.get_all_categories_admin()
    except Exception as e:
        logger.error(f"获取工具分类列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/tool-categories", response_model=CreateToolCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_tool_category(
    request: CreateToolCategoryRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """创建工具分类（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        category = common_tool_service.create_category(request)
        return CreateToolCategoryResponse(category=category)
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


@router.patch("/tool-categories/{category_id}", response_model=UpdateToolCategoryResponse)
async def update_tool_category(
    category_id: str,
    request: UpdateToolCategoryRequest,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """更新工具分类（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        category = common_tool_service.update_category(category_id, request)
        return UpdateToolCategoryResponse(category=category)
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


@router.delete("/tool-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool_category(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """删除工具分类（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        common_tool_service.delete_category(category_id)
        return None
    except ValueError as e:
        if "不存在" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        if "还有" in str(e) and "工具" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/tool-categories/{category_id}/move-up", response_model=MoveCategoryResponse)
async def move_category_up(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """上移分类（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        category = common_tool_service.move_category_up(category_id)
        return MoveCategoryResponse(message="分类已上移", category=category)
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


@router.post("/tool-categories/{category_id}/move-down", response_model=MoveCategoryResponse)
async def move_category_down(
    category_id: str,
    current_user: Annotated[UserInfo, Depends(require_admin)] = None,
):
    """下移分类（管理后台）"""
    try:
        common_tool_service = get_common_tool_service()
        category = common_tool_service.move_category_down(category_id)
        return MoveCategoryResponse(message="分类已下移", category=category)
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
