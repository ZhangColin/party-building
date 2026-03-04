# -*- coding: utf-8 -*-
"""
工具列表路由

提供工具列表查询接口，支持获取所有工具或按工具集过滤
"""
from fastapi import APIRouter, Depends
from src.models import ToolListResponse
from src.interfaces.dependencies import get_tool_service, get_current_user
from src.services.tool_service import ToolService

router = APIRouter()


@router.get("/tools", response_model=ToolListResponse, tags=["工具"])
async def get_tools(
    current_user = Depends(get_current_user),
    tool_service: ToolService = Depends(get_tool_service)
):
    """
    获取所有工具列表

    返回所有可见的工具，按分类组织
    """
    # 加载所有工具（只返回 visible=true 的工具）
    tools = tool_service.load_all_tools()

    # 按 category 聚合
    category_groups = tool_service.group_by_category(tools)

    # 将 Tool 对象转换为 ToolListItem 格式
    for category in category_groups:
        category['tools'] = [
            {
                'tool_id': tool.tool_id,
                'name': tool.name,
                'description': tool.description,
                'icon': tool.icon,
                'category': tool.category,
                'visible': tool.visible,
                'type': tool.type,
                'welcome_message': tool.welcome_message,
                'toolset_id': tool.toolset_id,
            }
            for tool in category['tools']
        ]

    return ToolListResponse(categories=category_groups)


@router.get("/toolsets/{toolset_id}/tools", response_model=ToolListResponse, tags=["工具"])
async def get_toolset_tools(
    toolset_id: str,
    current_user = Depends(get_current_user),
    tool_service: ToolService = Depends(get_tool_service)
):
    """
    获取指定工具集的工具列表

    Args:
        toolset_id: 工具集ID（如 ai_tools, teaching_researcher）

    Returns:
        指定工具集的工具列表，按分类组织
    """
    # 加载指定工具集的工具
    tools = tool_service.load_tools_by_toolset(toolset_id)
    category_groups = tool_service.group_by_category(tools, toolset_id=toolset_id)

    # 将 Tool 对象转换为 ToolListItem 格式
    for category in category_groups:
        category['tools'] = [
            {
                'tool_id': tool.tool_id,
                'name': tool.name,
                'description': tool.description,
                'icon': tool.icon,
                'category': tool.category,
                'visible': tool.visible,
                'type': tool.type,
                'welcome_message': tool.welcome_message,
                'toolset_id': tool.toolset_id,
            }
            for tool in category['tools']
        ]

    return ToolListResponse(categories=category_groups)
